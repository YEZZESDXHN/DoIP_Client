

class CanPluginAdapter(CANAdapter):
    def __init__(self): super().__init__("tosun", "tosun")

    def get_display_text(self, config):
        return f"{config['interface']} - {config['name']} - channel {config['channel']}  {config['sn']}"
