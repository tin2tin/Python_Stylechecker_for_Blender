bl_info = {
    "name": "Codestyle",
    "author": "tin2tin",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "Text Editor > Sidebar > Codestyle",
    "description": "Runs pep8 stylechecks on current document",
    "warning": "Pycodestyle must be installed in your Blender Python folder with ex. pip",
    "wiki_url": "https://github.com/tin2tin/Python_Stylechecker_for_Blender",
    "category": "Text Editor",
}


import bpy
import os
try:
    import pycodestyle
except ImportError:
    pycodestyle = None

import re
from bpy.props import PointerProperty, IntProperty, StringProperty, BoolProperty

ignores = {
    'pep8': [
        'E131',  # continuation line unaligned for hanging indent
        'W503',  # Line breaks should occur before a binary operator
        'W504',  # Line break occurred after a binary operator
        'E402',  # module level import not at top of file
    ]
}


class StringReport(pycodestyle.StandardReport):
    bl_idname = "text.report_pep8"
    bl_label = "PEP8 Codestyle"

    def get_failures(self):
        """
        Returns the list of failures, including source lines, as a formatted
        strings ready to be printed.
        """
        err_strings = []
        if self.total_errors > 0:
            self._deferred_print.sort()
            for line_number, offset, code, text, doc in self._deferred_print:
                err_strings.append(self._fmt % {
                    'path': self.filename,
                    'row': self.line_offset + line_number, 'col': offset + 1,
                    'code': code, 'text': text,
                })
                if line_number > len(self.lines):
                    line = ''
                else:
                    line = self.lines[line_number - 1]
                err_strings.append(line.rstrip())
                err_strings.append(re.sub(r'\S', ' ', line[:offset]) + '^')
        return err_strings


def getfunc(file, context):
    if not file:
        return []
    classes = []
    defs = []

    report = []
    failures = []
    linenumber = []
    character = []
    pep8opts = pycodestyle.StyleGuide(
        ignore=ignores['pep8'],
        max_line_length=120,
        format='pylint'
    ).options
    report = StringReport(pep8opts)
    failures = []
    checker = pycodestyle.Checker(file, options=pep8opts, report=report)
    checker.check_all()
    report = checker.report

    if report.get_file_results() > 0:
        failures.extend(report.get_failures())
        failures.append('')

    for l in failures:
        print(l)
        if l.find(':') == 1:
            start = 'py:'
            end = ': '
            linenumber = l[l.find(start) + len(start):l.rfind(end)]
            end = '] '
            error = l[l.rfind(end) + 2:]
            character = l.find('^')
            if error:
                classes.append([linenumber + ': ' + error.title(), linenumber, character])
    return classes


class TEXT_OT_pep8_button(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "text.pep8_button"
    bl_label = "Check Codestyle"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        old_filename = bpy.context.space_data.text.filepath
        filename = bpy.utils.script_path_user() + "temp_pep8.py"
        bpy.ops.text.save_as(filepath=filename, check_existing=False)
        bpy.types.Scene.pep8 = getfunc(filename, context)
        os.remove(filename)
        bpy.context.space_data.text.filepath = old_filename
        return {'FINISHED'}


class TEXT_PT_show_pep8(bpy.types.Panel):
    bl_space_type = 'TEXT_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Codestyle"
    bl_label = "PEP8 Codestyle"

    @classmethod
    def poll(cls, context):
        return context.area.spaces.active.type == "TEXT_EDITOR" and context.area.spaces.active.text

    def draw(self, context):
        layout = self.layout
        st = context.space_data
        layout.operator("text.pep8_button")
        items = bpy.types.Scene.pep8
        for it in items:
            cname = it[0]
            cline = it[1]
            layout = layout.column(align=True)
            layout.alignment = 'LEFT'
            layout.operator("text.class_viewer", text=cname).line = int(cline)


class TEXT_OT_class_viewer(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "text.class_viewer"
    bl_label = "Class Viewer"

    line: IntProperty(default=0, options={'HIDDEN'})
    character: IntProperty(default=0, options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        line = self.line
        character = self.character
        print(character)
        if line > 0:
            bpy.ops.text.jump(line=line)
        self.line = -1
        #  bpy.ops.text.cursor_set(line, character)#, line, character) # I wish this would work

        return {'FINISHED'}


classes = (
    TEXT_PT_show_pep8,
    TEXT_OT_class_viewer,
    TEXT_OT_pep8_button,
    )


def register():

    for i in classes:
        bpy.utils.register_class(i)
        bpy.types.Scene.pep8 = bpy.props.StringProperty()


def unregister():

    for i in classes:
        bpy.utils.unregister_class(i)
        del bpy.types.Scene.pep8


if __name__ == "__main__":
    register()
