from utils import import_kv
from kivy.uix.modalview import ModalView

import_kv(__file__)


class AppMenu(ModalView):
    def __init__(self, **kwargs):
        super(AppMenu, self).__init__(**kwargs)
