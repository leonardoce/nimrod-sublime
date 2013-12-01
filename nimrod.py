import sublime, sublime_plugin
import os, subprocess
import re

##Resources
# http://sublimetext.info/docs/en/extensibility/plugins.html
# http://www.sublimetext.com/docs/2/api_reference.html#sublime.View
# http://net.tutsplus.com/tutorials/python-tutorials/how-to-create-a-sublime-text-2-plugin/
# http://www.sublimetext.com/docs/plugin-examples

class LookupCommand(sublime_plugin.TextCommand):

    def idetool(self, cmd, filename, line, col, extra = ""):
        args = "nimrod --verbosity:0 idetools " \
             + cmd + " --track:" \
             + filename + "," + str(line) + "," + str(col) \
             + " " + filename + extra

        result = ""
        for result in os.popen(args): pass

        return result

    def lookup(self, filename, line, col):
        result = self.idetool("--def", filename, line, col)

        #Parse the result
        value = self.parse(result)

        self.open_definition(value[2], value[3], value[4])

    def parse(self, result):
        p = re.compile('^(?P<cmd>\S+)\s(?P<ast>\S+)\s(?P<symbol>\S+)\s(?P<type>[^\t]+)\s(?P<path>[^\t]+)\s(?P<line>\d+)\s(?P<col>\d+)\s(?P<description>\".+\")?')
        m = p.match(result)

        cmd = m.group("cmd")

        if cmd == "def":
            return (m.group("symbol"), m.group("type"),
             m.group("path"), m.group("line"), 
             m.group("col"), m.group("description"))

        return None


    def open_definition(self, filename, line, col):
        print(filename, line, col)
        win = self.view.window()
        arg = filename + ":" + str(line) + ":" + str(col)
        win.open_file(arg, sublime.ENCODED_POSITION | sublime.TRANSIENT)

    def run(self, edit):
        filename = self.view.file_name()
        sels = self.view.sel()

        for sel in sels:
            pos  = self.view.rowcol(sel.begin())
            line = pos[0]+1
            col  = pos[1]

            self.lookup(filename, line, col)