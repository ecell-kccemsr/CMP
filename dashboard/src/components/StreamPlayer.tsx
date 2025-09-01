import { FC, useEffect, useRef } from "react";
import Hls from "hls.js";
import { Box } from "@mantine/core";

interface StreamPlayerProps {
  streamUrl: string;
  autoplay?: boolean;
}

export const StreamPlayer: FC<StreamPlayerProps> = ({
  streamUrl,
  autoplay = true,
}) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const hlsRef = useRef<Hls | null>(null);

  useEffect(() => {
    if (!videoRef.current) return;

    const initPlayer = () => {
      if (hlsRef.current) {
        hlsRef.current.destroy();
      }

      if (Hls.isSupported()) {
        const hls = new Hls({
          maxBufferLength: 30,
          maxMaxBufferLength: 600,
          maxBufferSize: 60 * 1000 * 1000,
        });

        hlsRef.current = hls;
        hls.loadSource(streamUrl);
        if (videoRef.current) {
          hls.attachMedia(videoRef.current);

          hls.on(Hls.Events.MANIFEST_PARSED, () => {
            if (autoplay && videoRef.current) {
              videoRef.current.play().catch(console.error);
            }
          });
        }

        hls.on(Hls.Events.ERROR, (_, data) => {
          if (data.fatal) {
            switch (data.type) {
              case Hls.ErrorTypes.NETWORK_ERROR:
                hls.startLoad();
                break;
              case Hls.ErrorTypes.MEDIA_ERROR:
                hls.recoverMediaError();
                break;
              default:
                initPlayer();
                break;
            }
          }
        });
      } else if (
        videoRef.current &&
        videoRef.current.canPlayType("application/vnd.apple.mpegurl")
      ) {
        // For Safari
        videoRef.current.src = streamUrl;
        if (autoplay) {
          videoRef.current.play().catch(console.error);
        }
      }
    };

    initPlayer();

    return () => {
      if (hlsRef.current) {
        hlsRef.current.destroy();
      }
    };
  }, [streamUrl, autoplay]);

  return (
    <Box sx={{ width: "100%", height: "100%", background: "#000" }}>
      <video
        ref={videoRef}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "contain",
        }}
        controls
        playsInline
      />
    </Box>
  );
};
