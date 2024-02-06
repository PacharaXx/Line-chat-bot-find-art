from fastapi import FastAPI, UploadFile, Form, File
from starlette.responses import JSONResponse
from imageSearch import ImageSearcher
from PIL import Image
import io
import logging

app = FastAPI()

# Initialize the ImageSearcher
image_searcher = ImageSearcher(model_name='clip-ViT-B-32')
image_searcher.set_image_names(['list', 'of', 'image', 'paths'])  # Set image names
image_searcher.load_images()  # Load images

@app.post("/search_similar_images")
async def search_similar_images(
    target_image: UploadFile = File(...),
    user_id: str = Form(...),
):
    try:
        # Check if the uploaded file is an image
        if target_image.content_type not in ("image/jpeg", "image/png"):
            return JSONResponse(content={"error": "Invalid image format"}, status_code=400)

        # Read the uploaded image
        image_bytes = await target_image.read()
        target_image = Image.open(io.BytesIO(image_bytes))

        # Perform the image search
        most_similar_images = image_searcher.run_test(target_image)

        # Send the most similar images back to the user in the Line Chat
        # for image_path in most_similar_images:
        #     # Replace this with code to send messages or images back to the user using the Line Messaging API
        #     # You'll typically use the 'user_id' to specify the recipient of the message
        #     # For example:
        #     send_image_to_line_chat(user_id, image_path)

        return {"most_similar_images": most_similar_images}
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return JSONResponse(content={"error": "Internal server error"}, status_code=500)
