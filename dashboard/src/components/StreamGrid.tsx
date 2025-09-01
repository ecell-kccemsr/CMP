import { FC } from "react";
import { Grid, Paper, Text } from "@mantine/core";
import { useAppSelector } from "../store";
import { StreamPlayer } from "./StreamPlayer";
import { StreamMetadata } from "../types";

interface StreamGridProps {
  streams: StreamMetadata[];
  columns?: number;
}

export const StreamGrid: FC<StreamGridProps> = ({ streams, columns = 2 }) => {
  return (
    <Grid>
      {streams.map((stream) => (
        <Grid.Col key={stream.id} span={12 / columns}>
          <Paper p="md" radius="md" sx={{ height: "300px" }}>
            <StreamPlayer streamUrl={stream.hls_url} autoplay={true} />
            <Text size="sm" mt="xs" align="center">
              Classroom {stream.classroom_id} - {stream.stream_status}
            </Text>
          </Paper>
        </Grid.Col>
      ))}
    </Grid>
  );
};
