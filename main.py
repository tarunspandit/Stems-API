from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import base64
import subprocess
import zipfile
import os
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Server is up!"}
    
@app.post("/process_audio")
async def process_audio(file: UploadFile = File(...), num_stems: int = Form(...)):
    # Save the uploaded audio file to a temporary file
    with tempfile.NamedTemporaryFile(suffix=".wav") as temp_audio:
        temp_audio.write(file.file.read())
        temp_audio.seek(0)

        # Run Demucs v4 using subprocess
#        with tempfile.TemporaryDirectory() as output_dir:
#            subprocess_result = subprocess.run(
#                [
#                    "python",
#                    "-m",
#                    "demucs",
#                    "-d",
#                    "cpu",
#                    "-o",
#                    output_dir,  # Use output_dir as the output directory for Demucs
#                    temp_audio.name
#                ],
#                capture_output=True,
#                text=True,
#            )
#            if subprocess_result.returncode != 0:
#                print("Error in Demucs subprocess:", subprocess_result.stderr)
#                raise RuntimeError("Error occurred in Demucs subprocess")
        with tempfile.TemporaryDirectory() as output_dir:
            subprocess_result = subprocess.run(
                [
                    "python",
                    "-m",
                    "demucs",
                    "-d",
                    "cpu",
                    "-o",
                    output_dir,
                    temp_audio.name
                ],
                capture_output=True,
                text=True,
            )
            if subprocess_result.returncode != 0:
                print("Error in Demucs subprocess:", subprocess_result.stderr)
                raise RuntimeError("Error occurred in Demucs subprocess")
            tempon = os.path.splitext(os.path.basename(temp_audio.name))[0]
            # Print the contents of the output directory
            print("Contents of output_dir:", os.listdir(output_dir+"/htdemucs/"+tempon))

            # Create a zip file containing the separated stems
            with tempfile.NamedTemporaryFile(suffix=".zip") as temp_zip:
                with zipfile.ZipFile(temp_zip.name, mode='w') as zip_file:
                    for filename in os.listdir(output_dir+"/htdemucs/"+tempon):  # Use output_dir here
                        file_path = os.path.join(output_dir+"/htdemucs/"+tempon, filename)  # Use output_dir here
                        zip_file.write(file_path, filename)

                temp_zip.seek(0)
                output_stems = base64.b64encode(temp_zip.read()).decode("utf-8")

                return JSONResponse(content={"output_stems": output_stems})

#@app.post("/process_audio")
#async def process_audio(file: UploadFile = File(...), num_stems: int = Form(...)):
#    # Save the uploaded audio file to a temporary file
#    with tempfile.NamedTemporaryFile(suffix=".wav") as temp_audio:
#        temp_audio.write(file.file.read())
#        temp_audio.seek(0)
#
#        # Run Demucs v4 using subprocess
#        with tempfile.TemporaryDirectory() as output_dir:
#            subprocess_result = subprocess.run(
#                [
#                    "python",
#                    "-m",
#                    "demucs",
#                    "-d",
#                    "cpu",
#                    "-o",
#                    "/tmp/output_dir",
#                    temp_audio.name
#                ],
#                capture_output=True,
#                text=True,
#            )
#            if subprocess_result.returncode != 0:
#                print("Error in Demucs subprocess:", subprocess_result.stderr)
#                raise RuntimeError("Error occurred in Demucs subprocess")
#
#            # Create a zip file containing the separated stems
#            with tempfile.NamedTemporaryFile(suffix=".zip") as temp_zip:
#                with zipfile.ZipFile(temp_zip.name, mode='w') as zip_file:
#                    for filename in os.listdir("/tmp/output_dir"):
#                        file_path = os.path.join("/tmp/output_dir", filename)
#                        zip_file.write(file_path, filename)
#
#                temp_zip.seek(0)
#                output_stems = base64.b64encode(temp_zip.read()).decode("utf-8")
#
#                return JSONResponse(content={"output_stems": output_stems})

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 9002)))

