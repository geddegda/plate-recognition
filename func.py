import io, json
import oci
from fdk import response
import re

# Replace these placeholders with your own values
compartment_id = "<your_compartment_ocid>"
bucketName = "<your_bucket_name>"
nosql_db_id = "<your_nosql_table_ocid>"

signer = oci.auth.signers.get_resource_principals_signer()

client = oci.object_storage.ObjectStorageClient(config={}, signer=signer)
ai_vision_client = oci.ai_vision.AIServiceVisionClient(config={}, signer=signer)
nosql_client = oci.nosql.NosqlClient(config={}, signer=signer)

namespace = client.get_namespace().data

def handler(ctx, data: io.BytesIO=None):
    most_recent = get_most_recent(bucketName)
    if not most_recent:
        print("No objects found in the bucket.", flush=True)
        return response.Response(
            ctx,
            response_data=json.dumps({"error": "No objects found in the bucket"}),
            status_code=404,
            headers={"Content-Type": "application/json"}
        )
    number_plates = analyse_number_plate(namespace, bucketName, most_recent.name, compartment_id)

    for plate in number_plates["detectedPlates"]:
        try:
            nosql_client.update_row(
                table_name_or_id=nosql_db_id,
                update_row_details=oci.nosql.models.UpdateRowDetails(
                    value={
                        'plate': plate,
                        'detected_at': most_recent.time_created.isoformat(timespec='milliseconds'),
                        'source_image': most_recent.name,
                        'bucket_name': bucketName
                    }
                )
            )
        except Exception as e:
            print(f"Failed to insert plate {plate}: {e}", flush=True)

    return response.Response(
        ctx,
        response_data=json.dumps({
            "bucket": bucketName,
            "Most Recent": most_recent.name,
            "Last Uploaded": most_recent.time_created.isoformat(),
            "Text found": number_plates
        }),
        headers={"Content-Type": "application/json"}
    )

def get_most_recent(bucketName):
    response = client.list_objects(namespace, bucketName, fields="timeCreated", limit=1000)
    objs = response.data.objects

    if not objs:
        print("No objects found in the bucket.")
        return None

    most_recent = max(objs, key=lambda obj: obj.time_created)
    print(f"Most recent object: {most_recent.name}, uploaded at {most_recent.time_created}", flush=True)
    return most_recent

def analyse_number_plate(ns, bucketName, objectName, comp_id):
    analyze_image_response = ai_vision_client.analyze_image(
        analyze_image_details=oci.ai_vision.models.AnalyzeImageDetails(
            features=[oci.ai_vision.models.ImageTextDetectionFeature(feature_type="TEXT_DETECTION")],
            image=oci.ai_vision.models.ObjectStorageImageDetails(
                source="OBJECT_STORAGE",
                namespace_name=ns,
                bucket_name=bucketName,
                object_name=objectName
            ),
            compartment_id=comp_id
        )
    )
    image_text = analyze_image_response.data.image_text
    lines = [l.text for l in image_text.lines]
    full_text = " ".join(lines)

    print("Full text detected:", full_text, flush=True)
    plate_regex = r'\b[A-Z]{2}[0-9]{2} [A-Z]{3}\b'
    full_text = full_text.upper()
    uk_plates = re.findall(plate_regex, full_text)

    return {
        "detectedPlates": uk_plates
    }
