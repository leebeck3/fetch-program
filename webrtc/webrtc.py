import asyncio
from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from aiortc.contrib.media import MediaPlayer, MediaRecorder
import json

# Create a WebRTC peer connection
pcs = set()

async def index(request):
    """Serve the HTML client."""
    content = """
    <html>
    <body>
        <h1>WebRTC Example</h1>
        <video id="localVideo" autoplay muted></video>
        <video id="remoteVideo" autoplay></video>
        <script>
            const pc = new RTCPeerConnection();
            const localVideo = document.getElementById('localVideo');
            const remoteVideo = document.getElementById('remoteVideo');

            navigator.mediaDevices.getUserMedia({ video: true, audio: true }).then((stream) => {
                localVideo.srcObject = stream;
                stream.getTracks().forEach((track) => pc.addTrack(track, stream));
            });

            pc.ontrack = (event) => {
                remoteVideo.srcObject = event.streams[0];
            };

            async function negotiate() {
                const offer = await pc.createOffer();
                await pc.setLocalDescription(offer);

                const response = await fetch('/offer', {
                    method: 'POST',
                    body: JSON.stringify({
                        sdp: pc.localDescription.sdp,
                        type: pc.localDescription.type
                    }),
                    headers: { 'Content-Type': 'application/json' }
                });

                const answer = await response.json();
                await pc.setRemoteDescription(answer);
            }

            negotiate();
        </script>
    </body>
    </html>
    """
    return web.Response(content_type='text/html', text=content)

async def offer(request):
    """Handle the WebRTC offer from the client."""
    params = await request.json()
    offer = RTCSessionDescription(sdp=params['sdp'], type=params['type'])

    pc = RTCPeerConnection()
    pcs.add(pc)

    @pc.on("track")
    def on_track(track):
        print(f"Track received: {track.kind}")
        if track.kind == "video":
            local_video = MediaPlayer("testsrc=size=1280x720:rate=30", format="rawvideo", options={"video_size": "1280x720"})
            pc.addTrack(local_video.video)

    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return web.Response(
        content_type="application/json",
        text=json.dumps({
            "sdp": pc.localDescription.sdp,
            "type": pc.localDescription.type
        })
    )

async def cleanup(app):
    """Clean up WebRTC peer connections."""
    for pc in pcs:
        await pc.close()
    pcs.clear()

# Set up the web application
app = web.Application()
app.router.add_get('/', index)
app.router.add_post('/offer', offer)
app.on_shutdown.append(cleanup)

if __name__ == '__main__':
    web.run_app(app, port=8080)
