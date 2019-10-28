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
    bl_idname = "text.report_codestyle"
    bl_label = "Codestyle"

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
    codestyleopts = pycodestyle.StyleGuide(
        ignore=ignores['pep8'],
        max_line_length=120,
        format='pylint'
    ).options
    report = StringReport(codestyleopts)
    failures = []
    checker = pycodestyle.Checker(file, options=codestyleopts, report=report)
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
        if error and character > -1:
            classes.append([error.title(), linenumber, character])
    return classes


class TEXT_OT_codestyle_button(bpy.types.Operator):
    """Run Codestyle Check"""
    bl_idname = "text.codestyle_button"
    bl_label = "Check Codestyle"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        old_filename = bpy.context.space_data.text.filepath
        bpy.types.Scene.codestyle_name = old_filename
        filename = bpy.utils.script_path_user() + "temp_codestyle.py"
        bpy.ops.text.save_as(filepath=filename, check_existing=False)
        bpy.types.Scene.codestyle = getfunc(filename, context)
        os.remove(filename)
        bpy.context.space_data.text.filepath = old_filename
        return {'FINISHED'}


class TEXT_PT_show_codestyle(bpy.types.Panel):
    bl_space_type = 'TEXT_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Codestyle"
    bl_label = "Codestyle"

    @classmethod
    def poll(cls, context):
        return context.area.spaces.active.type == "TEXT_EDITOR" and context.area.spaces.active.text

    def draw(self, context):
        layout = self.layout
        st = context.space_data
        layout.use_property_split = False
        layout.operator("text.codestyle_button")
        print(bpy.context.space_data.text.filepath)
        if bpy.types.Scene.codestyle_name == bpy.context.space_data.text.filepath:
            items = bpy.types.Scene.codestyle
            for it in items:
                cname = it[0]
                cline = it[1]
                character = it[2]

                layout = layout.column(align=True)
                row = layout.row(align=True)
                row.alignment = 'LEFT'
                row.label(text="%4d " % int(cline))
                prop = row.operator("text.codestyle_jump", text="%s" % (cname), emboss=False)
                prop.line = int(cline)
                prop.character = int(character)
                row.label(text="")


class TEXT_OT_codestyle_jump(bpy.types.Operator):
    """Jump to line"""
    bl_idname = "text.codestyle_jump"
    bl_label = "Codestyle Jump"

    line: IntProperty(default=0, options={'HIDDEN'})
    character: IntProperty(default=0, options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        bpy.context.space_data.show_line_highlight = True
        line = self.line
        character = self.character
        print(character)
        if line > 0:
            bpy.ops.text.jump(line=line)
            curtxt = os.path.basename(bpy.context.space_data.text.filepath)
            bpy.data.texts[curtxt].select_set(line - 1, character, line - 1, character + 1)
        self.line = -1

        return {'FINISHED'}


classes = (
    TEXT_PT_show_codestyle,
    TEXT_OT_codestyle_jump,
    TEXT_OT_codestyle_button,
    )


def register():

    for i in classes:
        bpy.utils.register_class(i)
        bpy.types.Scene.codestyle = bpy.props.StringProperty()
        bpy.types.Scene.codestyle_name = bpy.props.StringProperty()


def unregister():

    for i in classes:
        bpy.utils.unregister_class(i)
        del bpy.types.Scene.codestyle
        del bpy.types.Scene.codestyle_name


if __name__ == "__main__":
    register()
