from resemblyzer import VoiceEncoder, preprocess_wav
import numpy as np
import io
import librosa
import streamlit as st


# =====================================================
# LOAD VOICE MODEL
# =====================================================
@st.cache_resource
def load_voice_encoder():

    try:
        print("Loading VoiceEncoder model...")
        return VoiceEncoder()

    except Exception as e:
        st.error(f'Voice model load failed: {e}')
        raise


# =====================================================
# OPTIONAL PRELOAD
# Call once during page/app load
# =====================================================
def preload_voice_model():

    try:
        load_voice_encoder()
        print("Voice model preloaded")

    except Exception as e:
        st.error(f'Voice preload failed: {e}')


# =====================================================
# GENERATE VOICE EMBEDDING
# =====================================================
def get_voice_embedding(audio_bytes):

    try:

        print("Getting voice embedding...")

        encoder = load_voice_encoder()

        print("Loading audio...")

        audio, sr = librosa.load(
            io.BytesIO(audio_bytes),
            sr=16000
        )

        print("Preprocessing audio...")

        wav = preprocess_wav(audio)

        print("Generating embedding...")

        embedding = encoder.embed_utterance(wav)

        return embedding.tolist()

    except Exception as e:

        st.error(f'Voice recog error: {e}')

        return None


# =====================================================
# IDENTIFY SPEAKER
# =====================================================
def identify_speaker(
    new_embedding,
    candidates_dict,
    threshold=0.65
):

    if new_embedding is None or not candidates_dict:
        return None, 0.0

    best_sid = None
    best_score = -1.0

    for sid, stored_embedding in candidates_dict.items():

        if stored_embedding:

            similarity = np.dot(
                new_embedding,
                stored_embedding
            )

            if similarity > best_score:

                best_score = similarity
                best_sid = sid

    if best_score >= threshold:
        return best_sid, best_score

    return None, best_score


# =====================================================
# BULK AUDIO PROCESSING
# =====================================================
def process_bulk_audio(
    audio_bytes,
    candidates_dict,
    threshold=0.60
):

    try:

        print("Starting bulk audio processing...")

        encoder = load_voice_encoder()

        print("Loading classroom audio...")

        audio, sr = librosa.load(
            io.BytesIO(audio_bytes),
            sr=16000
        )

        print("Splitting speech segments...")

        segments = librosa.effects.split(
            audio,
            top_db=30
        )

        identified_results = {}

        print(f"Segments found: {len(segments)}")

        for start, end in segments:

            if (end - start) < sr * 0.5:
                continue

            segment_audio = audio[start:end]

            wav = preprocess_wav(
                segment_audio
            )

            embedding = encoder.embed_utterance(
                wav
            )

            sid, score = identify_speaker(
                embedding,
                candidates_dict,
                threshold
            )

            if sid:

                if (
                    sid not in identified_results
                    or
                    score > identified_results[sid]
                ):

                    identified_results[sid] = score

        print("Bulk processing complete")

        return identified_results

    except Exception as e:

        st.error(f'Bulk process error: {e}')

        return {}