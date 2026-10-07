python
import streamlit as st
import whisper
import subprocess
import imageio_ffmpeg

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

st.set_page_config(page_title="Auto Caption App")

st.title("🎬 Auto Caption App")
st.write("Video upload karein aur automatic captions banayein.")

uploaded_file = st.file_uploader(
    "Apni video upload karein",
    type=["mp4", "mov", "avi", "mkv"]
)

if uploaded_file is not None:

    input_video = "input_video.mp4"
    output_video = "captioned_video.mp4"

    with open(input_video, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success("Video upload ho gayi! ✅")

    if st.button("Generate Captions 🚀"):

        with st.spinner("AI captions bana raha hai..."):

            model = whisper.load_model("base")

            result = model.transcribe(input_video)

            srt_file = "captions.srt"

            def format_time(seconds):
                hours = int(seconds // 3600)
                minutes = int((seconds % 3600) // 60)
                secs = int(seconds % 60)
                milliseconds = int((seconds - int(seconds)) * 1000)

                return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"

            with open(srt_file, "w", encoding="utf-8") as f:
                for i, segment in enumerate(result["segments"], start=1):

                    start = segment["start"]
                    end = segment["end"]
                    text = segment["text"].strip()

                    f.write(f"{i}\n")
                    f.write(f"{format_time(start)} --> {format_time(end)}\n")
                    f.write(f"{text}\n\n")

            subprocess.run([
                ffmpeg_exe,
                "-y",
                "-i", input_video,
                "-vf", "subtitles=captions.srt",
                "-c:a", "copy",
                output_video
            ], check=True)

        st.success("🎉 Captions successfully generate ho gaye!")

        st.video(output_video)

        with open(output_video, "rb") as f:
            st.download_button(
                "⬇️ Download Captioned Video",
                f,
                file_name="captioned_video.mp4",
                mime="video/mp4"
            )
