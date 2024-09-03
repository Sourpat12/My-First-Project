from scanip_api3 import *

# Obtain a reference to the application
app = App.GetInstance()

# Obtain the current document
doc = App.GetDocument()

# Specify Offset
offset = "1 mm"

# Define percentage and location names for acetabular spheres
percs = [25, 50, 100]
locs = ["PS", "PM", "PI"]

# Function to check if a mask exists by name
def mask_exists(doc, mask_name):
    try:
        mask = doc.GetMaskByName(mask_name)
        return mask is not None
    except Exception:
        return False

# Process each acetabular sphere
for perc in percs:
    for loc in locs:
        acetabular_sphere_name = f"{perc}% {loc} - Acetabular Sphere"
        acetabular_sphere_mask_name = f"{acetabular_sphere_name} (from surface)"
        pelvis_offset_mask_name = f"{perc}% {loc} - Pelvis - {offset} Offset"
        segment_offset_mask_name = f"{perc}% {loc} - Segment - {offset} Offset"

        try:
            # Convert Surfaces to Masks
            surface = doc.GetSurfaceByName(acetabular_sphere_name)

            # Wrap the single surface in a list
            surfaces = [surface]
            doc.CopySurfacesToMasks(surfaces, doc.AccurateManifold, False)
        
            # Subtract acetabular sphere from the pelvis mask
            boolStatement = f"(\"Full Pelvis\" MINUS \"{acetabular_sphere_mask_name}\")"
            doc.CreateMaskUsingBooleanExpression(boolStatement, doc.GetSliceIndices(doc.OrientationZX), doc.OrientationZX)
            doc.GetGenericMaskByName("Mask 1").SetName(pelvis_offset_mask_name)
            
            # Subtract pelvis without acetabular segment from Full Pelvis to make segment mask
            boolStatement = f"(\"Full Pelvis\" MINUS \"{pelvis_offset_mask_name}\")"
            doc.CreateMaskUsingBooleanExpression(boolStatement, doc.GetSliceIndices(doc.OrientationZX), doc.OrientationZX)
            doc.GetGenericMaskByName("Mask 1").SetName(segment_offset_mask_name)
            
            # Erode the segment mask by 1 mm in the x dimension
            doc.ApplyErodeFilter(doc.TargetMask, 1, 0, 0, 0.0)
            
            # Union the eroded segment with the pelvis offset mask
            boolStatement = f"(\"{segment_offset_mask_name}\" OR \"{pelvis_offset_mask_name}\")"
            doc.ReplaceMaskUsingBooleanExpression(boolStatement, doc.GetMaskByName(pelvis_offset_mask_name), doc.GetSliceIndices(doc.OrientationZX), doc.OrientationZX)
        
        except Exception as e:
            app.ShowMessage(f"An error occurred: {str(e)}", "Error")
