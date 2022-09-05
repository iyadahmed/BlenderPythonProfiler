import bpy
import cProfile
import io
import pstats
from pstats import SortKey

bl_info = {
    "name": "Blender Python Profiler",
    "description": "Profile Your Add-ons Easily",
    "author": "Iyad Ahmed",
    "version": (0, 1),
    "blender": (3, 2, 2),
    "location": "Text Editor > Profile",
    "warning": "",  # used for warning icon and text in addons panel
    "doc_url": "",
    "tracker_url": "",
    "support": "COMMUNITY",
    "category": "Scripting",
}

profile = cProfile.Profile()


class BPP_OT_enable_profiling(bpy.types.Operator):
    bl_idname = "bpp.enable"
    bl_label = "Profiling: Enable"

    def execute(self, context):
        profile.enable()
        return {"FINISHED"}


class BPP_OT_disable_profiling(bpy.types.Operator):
    bl_idname = "bpp.disable"
    bl_label = "Profiling: Disable"

    def execute(self, context):
        profile.disable()
        return {"FINISHED"}


class BPP_OT_print_stats(bpy.types.Operator):
    bl_idname = "bpp.print"
    bl_label = "Profiling: Print Statistics"

    def execute(self, context):
        s = io.StringIO()
        sortby = SortKey.CUMULATIVE
        ps = pstats.Stats(profile, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())
        return {"FINISHED"}


class BPP_PT_main(bpy.types.Panel):
    bl_label = "Profile"
    bl_category = "Profile"
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout

        layout.operator("bpp.enable", text="Enable")
        layout.operator("bpp.disable", text="Disable")
        layout.operator("bpp.print", text="Print Statistics")


classes = [BPP_OT_disable_profiling,
           BPP_OT_enable_profiling,
           BPP_OT_print_stats,
           BPP_PT_main]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
