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
is_profile_enabled = False


class BPP_OT_toggle_profiling(bpy.types.Operator):
    """Toggle profiling"""
    bl_idname = "bpp.toggle_profiling"
    bl_label = "Profiling: Toggle"

    def execute(self, context):
        global is_profile_enabled
        if not is_profile_enabled:
            profile.enable()
            is_profile_enabled = True
        else:
            profile.disable()
            is_profile_enabled = False
        return {"FINISHED"}


class BPP_OT_export_stats(bpy.types.Operator):
    bl_idname = "bpp.export"
    bl_label = "Profiling: Export Statistics"

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        with open(self.filepath, 'w') as file:
            sortby = SortKey.CUMULATIVE
            ps = pstats.Stats(profile, stream=file).sort_stats(sortby)
            ps.print_stats()
        return {"FINISHED"}


class BPP_PT_main(bpy.types.Panel):
    bl_label = "Profile"
    bl_category = "Profile"
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout

        layout.operator("bpp.toggle_profiling",
                        text="Stop" if is_profile_enabled else "Start",
                        icon="PAUSE" if is_profile_enabled else "PLAY")
        layout.operator("bpp.export", text="Export Statistics")


classes = [BPP_OT_toggle_profiling,
           BPP_OT_export_stats,
           BPP_PT_main]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
