import wx
import gettext
_ = gettext.gettext
from datetime import datetime

class View(wx.Frame):
    def __init__(self, parent, controller):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=_(u"E-Health ID Generator"),
                          pos=wx.DefaultPosition, size=wx.Size(500, 470),
                          style=wx.DEFAULT_FRAME_STYLE & ~(wx.MAXIMIZE_BOX | wx.RESIZE_BORDER) | wx.TAB_TRAVERSAL)

        self.controller = controller
        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
        self.SetBackgroundColour(wx.Colour(240, 240, 240))

        # Main sizer
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Header: Title and Date/Time
        self.header_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.title_label = wx.StaticText(self, wx.ID_ANY, _(u"E-Health ID Generator"), wx.DefaultPosition, wx.DefaultSize, 0)
        self.title_label.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.header_sizer.Add(self.title_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)

        self.header_sizer.AddStretchSpacer()

        self.datetime_label = wx.StaticText(self, wx.ID_ANY, "", wx.DefaultPosition, wx.Size(200, -1), 0)
        self.datetime_label.SetForegroundColour(wx.Colour(0, 0, 255))  # Blue text
        self.datetime_label.SetBackgroundColour(wx.Colour(240, 248, 255))  # Light blue background
        self.datetime_label.SetFont(wx.Font(10, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.header_sizer.Add(self.datetime_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)  # Added padding via sizer
        self.main_sizer.Add(self.header_sizer, 0, wx.EXPAND | wx.ALL, 10)

        # Mode Selection with Radio Buttons
        self.mode_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.radio_generate_id = wx.RadioButton(self, wx.ID_ANY, _(u"Generate ID"), wx.DefaultPosition, wx.DefaultSize, wx.RB_GROUP)
        self.radio_encrypt = wx.RadioButton(self, wx.ID_ANY, _(u"Decrypt/Encrypt File"), wx.DefaultPosition, wx.DefaultSize, 0)
        self.radio_generate_keys = wx.RadioButton(self, wx.ID_ANY, _(u"Generate Keys"), wx.DefaultPosition, wx.DefaultSize, 0)
        self.mode_sizer.Add(self.radio_generate_id, 0, wx.ALL, 5)
        self.mode_sizer.Add(self.radio_encrypt, 0, wx.ALL, 5)
        self.mode_sizer.Add(self.radio_generate_keys, 0, wx.ALL, 5)
        self.main_sizer.Add(self.mode_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        # Content Panel (Stack Panel)
        self.content_panel = wx.Panel(self, wx.ID_ANY)
        self.content_sizer = wx.BoxSizer(wx.VERTICAL)
        self.content_panel.SetSizer(self.content_sizer)
        self.main_sizer.Add(self.content_panel, 1, wx.EXPAND | wx.ALL, 5)

        # Generate ID Section
        self.generate_id_panel = wx.Panel(self.content_panel, wx.ID_ANY)
        self.generate_id_sizer = wx.BoxSizer(wx.VERTICAL)

        # Seed Input
        self.seed_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.seed_label = wx.StaticText(self.generate_id_panel, wx.ID_ANY, _(u"Seed (Optional):"), wx.DefaultPosition, wx.DefaultSize, 0)
        self.seed_label.SetToolTip(wx.ToolTip("A seed ensures the same IDs are generated each time. Leave blank for random generation."))
        self.seed_sizer.Add(self.seed_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.seed_input = wx.TextCtrl(self.generate_id_panel, wx.ID_ANY, "", wx.DefaultPosition, wx.DefaultSize, 0)
        self.seed_sizer.Add(self.seed_input, 1, wx.ALL, 5)
        self.generate_id_sizer.Add(self.seed_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # Number of IDs
        self.num_ids_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.num_ids_label = wx.StaticText(self.generate_id_panel, wx.ID_ANY, _(u"Number of IDs:"), wx.DefaultPosition, wx.DefaultSize, 0)
        self.num_ids_sizer.Add(self.num_ids_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.num_ids_input = wx.TextCtrl(self.generate_id_panel, wx.ID_ANY, "", wx.DefaultPosition, wx.DefaultSize, 0)
        self.num_ids_sizer.Add(self.num_ids_input, 1, wx.ALL, 5)
        self.generate_id_sizer.Add(self.num_ids_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # Save to Destination Path
        self.dest_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.dest_label = wx.StaticText(self.generate_id_panel, wx.ID_ANY, _(u"Save to Destination:"), wx.DefaultPosition, wx.DefaultSize, 0)
        self.dest_sizer.Add(self.dest_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.dest_picker = wx.DirPickerCtrl(self.generate_id_panel, wx.ID_ANY, wx.EmptyString, _(u"Select destination directory"), wx.DefaultPosition, wx.DefaultSize, wx.DIRP_DEFAULT_STYLE)
        self.dest_sizer.Add(self.dest_picker, 1, wx.ALL, 5)
        self.generate_id_sizer.Add(self.dest_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # File Type Selection
        self.type_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.type_label = wx.StaticText(self.generate_id_panel, wx.ID_ANY, _(u"Save As Type:"), wx.DefaultPosition, wx.DefaultSize, 0)
        self.type_sizer.Add(self.type_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        file_types = [".csv", ".txt", ".json", ".xlsx"]
        self.type_choice = wx.Choice(self.generate_id_panel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, file_types, 0)
        self.type_choice.SetSelection(0)
        self.type_sizer.Add(self.type_choice, 1, wx.ALL, 5)
        self.generate_id_sizer.Add(self.type_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # Generate Button
        self.generate_id_btn = wx.Button(self.generate_id_panel, wx.ID_ANY, _(u"Generate IDs"), wx.DefaultPosition, wx.DefaultSize, 0)
        self.generate_id_sizer.Add(self.generate_id_btn, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        self.generate_id_panel.SetSizer(self.generate_id_sizer)

        # Encrypt/Decrypt Section
        self.encrypt_panel = wx.Panel(self.content_panel, wx.ID_ANY)
        self.encrypt_sizer = wx.BoxSizer(wx.VERTICAL)

        # Description
        self.encrypt_desc = wx.StaticText(self.encrypt_panel, wx.ID_ANY, _(u"Exchanging information between two users without exposing content to a third person."), wx.DefaultPosition, wx.DefaultSize, 0)
        self.encrypt_desc.Wrap(400)
        self.encrypt_sizer.Add(self.encrypt_desc, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        # Select File
        self.select_file_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.select_file_label = wx.StaticText(self.encrypt_panel, wx.ID_ANY, _(u"Select File:"), wx.DefaultPosition, wx.DefaultSize, 0)
        self.select_file_sizer.Add(self.select_file_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.file_picker = wx.FilePickerCtrl(self.encrypt_panel, wx.ID_ANY, wx.EmptyString, _(u"Select a file"), u"*.*", wx.DefaultPosition, wx.DefaultSize, wx.FLP_DEFAULT_STYLE)
        self.select_file_sizer.Add(self.file_picker, 1, wx.ALL, 5)
        self.encrypt_sizer.Add(self.select_file_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # Select Key
        self.select_key_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.select_key_label = wx.StaticText(self.encrypt_panel, wx.ID_ANY, _(u"Select Key:"), wx.DefaultPosition, wx.DefaultSize, 0)
        self.select_key_sizer.Add(self.select_key_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.key_picker = wx.FilePickerCtrl(self.encrypt_panel, wx.ID_ANY, wx.EmptyString, _(u"Select a key file"), u"*.*", wx.DefaultPosition, wx.DefaultSize, wx.FLP_DEFAULT_STYLE)
        self.select_key_sizer.Add(self.key_picker, 1, wx.ALL, 5)
        self.encrypt_sizer.Add(self.select_key_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # Encrypt/Decrypt Radio Buttons
        self.encrypt_radio_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.radio_encrypt_action = wx.RadioButton(self.encrypt_panel, wx.ID_ANY, _(u"Encrypt"), wx.DefaultPosition, wx.DefaultSize, wx.RB_GROUP)
        self.radio_decrypt_action = wx.RadioButton(self.encrypt_panel, wx.ID_ANY, _(u"Decrypt"), wx.DefaultPosition, wx.DefaultSize, 0)
        self.encrypt_radio_sizer.Add(self.radio_encrypt_action, 0, wx.ALL, 5)
        self.encrypt_radio_sizer.Add(self.radio_decrypt_action, 0, wx.ALL, 5)
        self.encrypt_sizer.Add(self.encrypt_radio_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        # Process Button
        self.process_btn = wx.Button(self.encrypt_panel, wx.ID_ANY, _(u"Process"), wx.DefaultPosition, wx.DefaultSize, 0)
        self.encrypt_sizer.Add(self.process_btn, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        self.encrypt_panel.SetSizer(self.encrypt_sizer)

        # Generate Keys Section
        self.generate_keys_panel = wx.Panel(self.content_panel, wx.ID_ANY)
        self.generate_keys_sizer = wx.BoxSizer(wx.VERTICAL)

        # Output Directory for Keys
        self.key_output_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.key_output_label = wx.StaticText(self.generate_keys_panel, wx.ID_ANY, _(u"Save Keys To:"), wx.DefaultPosition, wx.DefaultSize, 0)
        self.key_output_sizer.Add(self.key_output_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.key_output_picker = wx.DirPickerCtrl(self.generate_keys_panel, wx.ID_ANY, wx.EmptyString, _(u"Select output directory"), wx.DefaultPosition, wx.DefaultSize, wx.DIRP_DEFAULT_STYLE)
        self.key_output_sizer.Add(self.key_output_picker, 1, wx.ALL, 5)
        self.generate_keys_sizer.Add(self.key_output_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # Generate Keys Button
        self.generate_keys_btn = wx.Button(self.generate_keys_panel, wx.ID_ANY, _(u"Generate Keys"), wx.DefaultPosition, wx.DefaultSize, 0)
        self.generate_keys_sizer.Add(self.generate_keys_btn, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        self.generate_keys_panel.SetSizer(self.generate_keys_sizer)

        # Footer
        self.footer_label = wx.StaticText(self, wx.ID_ANY, _(u"Copyright 2025 @Ehealth Hub."), wx.DefaultPosition, wx.DefaultSize, 0)
        self.footer_label.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL))
        self.main_sizer.Add(self.footer_label, 0, wx.ALIGN_CENTER | wx.ALL, 5)

        self.SetSizer(self.main_sizer)
        self.Layout()
        self.Centre(wx.BOTH)

        # Initialize timer
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.update_datetime, self.timer)
        self.timer.Start(1000)

        # Bind close event to stop the timer
        self.Bind(wx.EVT_CLOSE, self.on_close)

    def update_datetime(self, event):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.datetime_label.SetLabel(f"Date: {current_time}")
        self.Layout()  # Ensure the label updates and refreshes properly

    def on_close(self, event):
        self.timer.Stop()
        event.Skip()

    def get_seed(self):
        return self.seed_input.GetValue()

    def get_num_ids(self):
        return self.num_ids_input.GetValue()

    def get_dest_path(self):
        return self.dest_picker.GetPath()

    def get_file_type(self):
        return self.type_choice.GetStringSelection()

    def get_file_path(self):
        return self.file_picker.GetPath()

    def get_key_path(self):
        return self.key_picker.GetPath()

    def get_encrypt_action(self):
        return "Encrypt" if self.radio_encrypt_action.GetValue() else "Decrypt"

    def get_key_output_path(self):
        return self.key_output_picker.GetPath()

    def show_message(self, message, caption, style):
        wx.MessageBox(message, caption, style)

    def switch_panel(self, panel):
        # Hide all children of the content panel
        for child in self.content_panel.GetChildren():
            child.Hide()
        
        # Detach all items from the sizer without deleting them
        self.content_sizer.Clear(False)
        
        # Show the new panel and add it to the sizer
        panel.Show()
        self.content_sizer.Add(panel, 1, wx.EXPAND | wx.ALL, 5)
        
        # Force layout updates
        self.content_panel.Layout()
        self.Layout()
        self.Refresh()