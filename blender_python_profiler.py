import bpy
import cProfile
import io
import pstats
from pstats import SortKey
import addon_utils
import os

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

profile = None


class BPP_OT_start_profiling(bpy.types.Operator):
    """Start profiling"""
    bl_idname = "bpp.start_profiling"
    bl_label = "Profiling: Start"

    def execute(self, context):
        global profile
        assert profile is None
        profile = cProfile.Profile()
        profile.enable()
        return {"FINISHED"}


class BPP_OT_stop_profiling_and_export_stats(bpy.types.Operator):
    """Stop profiling and export statistics"""
    bl_idname = "bpp.stop_profiling_and_export_stats"
    bl_label = "Export Statistics"

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    stats_regex_filter: bpy.props.StringProperty(default="", options={"HIDDEN", "SKIP_SAVE"})

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        global profile
        assert profile is not None
        with open(self.filepath, 'w') as file:
            sortby = SortKey.CUMULATIVE
            ps = pstats.Stats(profile, stream=file).sort_stats(sortby)
            ps.print_stats(self.stats_regex_filter)
        profile = None
        return {"FINISHED"}


class BPP_PT_main(bpy.types.Panel):
    bl_label = "Profile"
    bl_category = "Profile"
    bl_space_type = "TEXT_EDITOR"
    bl_region_type = "UI"

    def draw(self, context):
        global profile
        layout = self.layout
        addon_prefs = context.preferences.addons[__name__].preferences

        layout.prop(addon_prefs, "filter_stats_by_addon")
        stats_regex_filter = ""
        if addon_prefs.filter_stats_by_addon:
            layout.prop(addon_prefs, "addon")
            stats_regex_filter = os.sep + addon_prefs.addon + os.sep

        if profile is None:
            layout.operator("bpp.start_profiling", text="Start", icon="PLAY")
        else:
            op = layout.operator("bpp.stop_profiling_and_export_stats", text="Stop", icon="EXPORT")
            op.stats_regex_filter = stats_regex_filter


# Stores addon enum items to avoid crash because of string garbage collection
addon_items = []


def get_addon_items(self, context):
    global addon_items
    addon_items.clear()
    i = 0
    for module in addon_utils.modules():
        loaded_default, loaded_state = addon_utils.check(module.__name__)
        if loaded_state:
            addon_items.append((module.__name__, module.bl_info["name"], "", i))
            i += 1

    return addon_items


class BPP_preferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    addon: bpy.props.EnumProperty(name="Add-on", items=get_addon_items)
    filter_stats_by_addon: bpy.props.BoolProperty(name="Filter by add-on",
                                                  description="Only export statistics for the selected add-on",
                                                  default=True)


classes = [BPP_OT_start_profiling,
           BPP_OT_stop_profiling_and_export_stats,
           BPP_preferences,
           BPP_PT_main]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
