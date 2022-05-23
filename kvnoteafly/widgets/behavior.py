from __future__ import annotations

from utils import import_kv

import_kv(__file__)

from typing import Any, Iterable, Optional
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
from kivy.properties import (
    BooleanProperty,
    ColorProperty,
    NumericProperty,
    ReferenceListProperty,
    StringProperty,
)
from kivy.uix.label import Label


def color_norm(color) -> Iterable[float, float, float, float]:
    def color_str_components(s: str) -> Iterable[float, float, float, float]:
        """Return hex as 1.0 * 4"""
        s = s.removeprefix("#")
        # Groups of two
        components_hex = zip(*[iter(s)] * 2)
        has_opacity = False
        for i, comp in enumerate(components_hex):
            if i == 3:
                has_opacity = True
                yield int("".join(comp), 16) / 255
                continue
            yield int("".join(comp), 16) / 255
        if not has_opacity:
            yield 1.0

    def color_float_components(
        s: tuple[int] | tuple[float],
    ) -> Iterable[float, float, float, float]:
        """Return r, g, b (0.0-1.0) as (0-1) and opacity as (0-1)"""
        has_opacity = False
        for i, comp in enumerate(s):
            if i == 3:
                has_opacity = True
                yield comp
                continue
            yield comp
        if not has_opacity:
            yield 1.0

    if isinstance(color, str):
        components = color_str_components(color)
    else:
        components = color_float_components(color)

    return components


def text_contrast(background_color, threshold, highlight_color: Optional[Any] = None):
    """
    Set text as white or black depending on bg

    """
    if not highlight_color:
        r, g, b, opacity = color_norm(background_color)
        brightness = (r * 0.299 + g * 0.587 + b * 0.114 + (1 - opacity)) * 255
    else:
        hl_norm = color_norm(highlight_color)
        bg_norm = color_norm(background_color)

        r_hl, g_hl, b_hl, opacity_hl = hl_norm
        r_bg, g_bg, b_bg, opacity_bg = bg_norm

        # https://stackoverflow.com/questions/726549/algorithm-for-additive-color-mixing-for-rgb-values
        opacity = 1 - (1 - opacity_hl) * (1 - opacity_bg)
        r = r_hl * opacity_hl / opacity + r_bg * opacity_bg * (1 - opacity_hl) / opacity
        g = g_hl * opacity_hl / opacity + g_bg * opacity_bg * (1 - opacity_hl) / opacity
        b = b_hl * opacity_hl / opacity + b_bg * opacity_bg * (1 - opacity_hl) / opacity

        # https://stackoverflow.com/questions/3942878/how-to-decide-font-color-in-white-or-black-depending-on-background-color
        brightness = (r * 0.299 + g * 0.587 + b * 0.114 + (1 - opacity)) * 255
    if brightness > threshold:
        return "#000000"
    else:
        return "#ffffff"


class LabelAutoContrast(Label):
    """
    Label that changes text color to optimize contrast
    """

    bg_color = ColorProperty()
    text_color = StringProperty("#ffffff")
    text_threshold = NumericProperty(186)
    _raw_text = StringProperty()

    def __init__(self, **kwargs):
        if "text" in kwargs:
            text = kwargs.pop("text")
        else:
            text = ""
        kwargs.update({"_raw_text": text, "text": text})
        super().__init__(**kwargs)

    def on_bg_color(self, instance, value):
        self.text_color = text_contrast(self.bg_color, self.text_threshold, None)

    def on_text_color(self, instance, value):
        self.text = f"[color={self.text_color}]{self._raw_text}[/color]"


class LabelHighlight(LabelAutoContrast):
    """
    Label that draws background sized to extents if highlight is set True

    Attributes
    ----------

    y_extent : The extent of the text in the y-axis
    x_extent : The extent of the text in the x-axis
    extents: ReferenceListProperty of x_extent, y_extent
    highlight: Toggles highlighting behavior
    bg_color: Color of the background. Since highlighting is mostly opaque, this is used for the text contrast check.
    highlight_color: Color of highlighting
    text_color: Either white or black. Auto color based on contrast of highlight_color and bg_color
    text_threshold: Threshold to change text_color
    font_family:
    _raw_text: Holds text before applying any markup. Required since get_extents does not remove markup.
    """

    y_extent = NumericProperty()
    x_extent = NumericProperty()
    extents = ReferenceListProperty(x_extent, y_extent)
    highlight = BooleanProperty(False)
    highlight_color = ColorProperty()

    def __init__(self, **kwargs):
        if "text" in kwargs:
            text = kwargs.pop("text")
        else:
            text = ""
        kwargs.update({"_raw_text": text, "text": text})
        super(LabelHighlight, self).__init__(**kwargs)

    def on_highlight(self, instance, value):
        if not value:
            self.unbind(texture_size=self.get_extents)
        else:
            self.bind(texture_size=self.get_extents)

    def on_highlight_color(self, instance, value):
        if self.highlight:
            self.text_color = text_contrast(
                self.bg_color, self.text_threshold, self.highlight_color
            )

    def on_bg_color(self, instance, value):
        if self.highlight:
            self.text_color = text_contrast(
                self.bg_color, self.text_threshold, self.highlight_color
            )

    def on_text_color(self, instance, value):
        if self.highlight:
            self.text = f"[color={self.text_color}]{self._raw_text}[/color]"

    def get_extents(self, instance, value):
        # Texture created
        # We have to remove markup
        w, h = self._label.get_extents(self._raw_text)

        # Now we can draw our codespan background
        self.x_extent = w + (2 * self.padding_x)
        self.y_extent = h + self.padding_y

    def on_extents(self, instance, value):
        Clock.schedule_once(self.draw_bg_extents)

    def get_x(self):
        if self.halign == "left":
            return self.center_x - self.texture_size[0] * 0.5
        elif self.halign == "center":
            return self.center_x - self.x_extent * 0.5
        elif self.halign == "right":
            return self.texture_size[0] - self.x_extent + (4 * self.padding_x)
        else:
            return self.center_x

    def get_y(self):
        return (self.center_y - self.texture_size[1] * 0.5) + (self.padding_y * 0.5)

    def draw_bg_extents(self, *args, **kwargs):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.highlight_color)
            RoundedRectangle(
                pos=(self.get_x(), self.get_y()), size=self.extents, radius=(3,)
            )