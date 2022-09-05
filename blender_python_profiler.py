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

filter_stats_by_addon_prop = bpy.props.BoolProperty(name="Filter by add-on",
                                                    description="Only export statistics for the selected add-on",
                                                    default=True)

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


addon_prop = bpy.props.EnumProperty(name="Add-on", items=get_addon_items)

sorting_criteria_prop = bpy.props.EnumProperty(name="Sorting criteria", items=[
    (SortKey.TIME, "Total Time",
     "Total time spent in the given function (and excluding time made in calls to sub-functions)", 0),
    (SortKey.CALLS, "Number Of Calls", "Number of calls", 1),
    (SortKey.PCALLS, "Time Per Call", "Total time divided by number of calls", 2),
    (SortKey.CUMULATIVE, "Cumulative Time",
     "Cumulative time spent in a function and all subfunctions (from invocation till exit). This figure is accurate even for recursive functions",
     3)
], default=SortKey.CUMULATIVE)


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

    # Allow setting properties in export dialog for convenience
    filter_stats_by_addon: filter_stats_by_addon_prop
    addon: addon_prop
    sorting_criteria: sorting_criteria_prop

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        global profile
        assert profile is not None

        regex_filter = (os.sep + self.addon + os.sep) if self.filter_stats_by_addon else ""
        with open(self.filepath, 'w') as file:
            ps = pstats.Stats(profile, stream=file)
            ps.sort_stats(self.sorting_criteria)
            ps.print_stats(regex_filter)

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
        if addon_prefs.filter_stats_by_addon:
            layout.prop(addon_prefs, "addon")

        layout.prop(addon_prefs, "sorting_criteria", text="Sort by")

        if profile is None:
            layout.operator("bpp.start_profiling", text="Start", icon="PLAY")
        else:
            op = layout.operator("bpp.stop_profiling_and_export_stats", text="Stop and Export", icon="EXPORT")
            op.sorting_criteria = addon_prefs.sorting_criteria
            op.filter_stats_by_addon = addon_prefs.filter_stats_by
            op.addon = addon_prefs.addon


class BPP_preferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    addon: addon_prop
    filter_stats_by_addon: filter_stats_by_addon_prop
    sorting_criteria: sorting_criteria_prop


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
