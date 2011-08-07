#!/usr/bin/python

import sys
import pygtk
pygtk.require('2.0')
import gtk

import testlibrary


class SpicelibTestGui:
    def __init__(self, lib_filename):
        self.filename = lib_filename
        self.library = testlibrary.modellibrary(self.filename)
        self.create_gui()
        self.load_models()

    def main(self):
        gtk.main()

    def create_gui(self):
        # create a new window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("delete_event", self.delete_event)
        self.window.connect("destroy", self.destroy)
        self.window.set_border_width(5)

        ## container for all elements
        vbox = gtk.VBox()
        self.window.add(vbox)

        ## upper hbox with devices and buttons
        hbox = gtk.HBox()
        hbox.set_homogeneous(True)
        vbox.pack_start(hbox, True, True, 5)

        ## upper left vbox with devices
        vbox1 = gtk.VBox()
        hbox.pack_start(vbox1, True, True, 5)
        scroll1 = gtk.ScrolledWindow()
        self.window.set_geometry_hints(vbox1, min_width=100)
        vbox1.pack_start(scroll1)

        ## Model text view
        self.model_text = gtk.TextView()
        self.model_text_buffer = gtk.TextBuffer()
        self.model_text_buffer.set_text('Hello World1!')
        self.model_text.set_buffer(self.model_text_buffer)
        scroll2 = gtk.ScrolledWindow()
        hbox.pack_start(scroll2, True, True, 5)
        scroll2.add(self.model_text)
        
        ## upper right vbox with model definition and test buttons
        vbox2 = gtk.VBox()
        hbox.pack_start(vbox2, True, True, 5)
        
        ## treeview for the model list
        self.model_list = gtk.ListStore(str)
        self.model_tree = gtk.TreeView(self.model_list)
        tvcolumn = gtk.TreeViewColumn('Device')
        self.model_tree.append_column(tvcolumn)
        cell = gtk.CellRendererText()
        tvcolumn.pack_start(cell,True)
        tvcolumn.add_attribute(cell, 'text', 0)
        scroll1.add(self.model_tree)
        self.model_tree.connect('cursor-changed', self.callback_select, None)

        ## device definition text view
        self.device_text = gtk.TextView()
        self.device_text_buffer = gtk.TextBuffer()
        self.device_text_buffer.set_text('Hello World2!')
        self.device_text.set_buffer(self.device_text_buffer)
        scroll3 = gtk.ScrolledWindow()
        vbox2.pack_start(scroll3, True, True, 5)
        scroll3.add(self.device_text)

        ## tester buttons
        button_test = gtk.Button("test model definition")
        button_test.connect("clicked", self.callback_test, None)
        vbox2.pack_start(button_test, False, False, 5)

        ## update checksum button
        button_sign = gtk.Button('update library golden checksum')
        button_sign.connect("clicked", self.callback_sign, None)
        vbox2.pack_start(button_sign, False, False, 5)

        ## html status widget in the bottom
        # TBD

        # The final step is to display this newly created widgets
        self.window.show_all()

    def load_models(self):
        for model in sorted(self.library.modelparts.keys()):
            self.model_list.append([model])

    def callback_select(self, treeview, data=None):
        path = treeview.get_cursor()[0]
        device = self.model_list[path][0]
        devicetext = self.library.get_devicetext(device)
        self.device_text_buffer.set_text(devicetext)
        modeltext = self.library.get_modeltext(device)
        self.model_text_buffer.set_text(modeltext)

    def callback_test(self, widget, data=None):
        path = self.model_tree.get_cursor()[0]
        model = self.model_list[path][0]
        self.library.test_single(model)


    def callback_sign(self, widget, data=None):
        print 'callback_sign'


    def out_of_range(self):
        d = gtk.MessageDialog(parent=self.window, flags=gtk.DIALOG_MODAL,
                              type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_CLOSE,
                              message_format='Point number out of range')

        d.run()
        d.destroy()

    def delete_event(self, widget, event, data=None):
        return False

    def destroy(self, widget, data=None):
        print "destroy signal occurred"
        gtk.main_quit()


if __name__ == "__main__":
    filename = sys.argv[1]
    app = SpicelibTestGui(filename)
    app.main()
