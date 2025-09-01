import { useEffect, useState } from "react";
import {
  Container,
  Title,
  Text,
  Button,
  Group,
  Stack,
  Select,
} from "@mantine/core";
import { useAppDispatch, useAppSelector } from "../store";
import { fetchStreams } from "../store/slices/streamSlice";
import { StreamGrid } from "../components/StreamGrid";
import { RootState } from "../types";

export function CameraView() {
  const dispatch = useAppDispatch();
  const { streams, loading, error } = useAppSelector(
    (state: RootState) => state.streams
  );
  const [gridColumns, setGridColumns] = useState(2);

  useEffect(() => {
    dispatch(fetchStreams());
    const interval = setInterval(() => {
      dispatch(fetchStreams());
    }, 30000); // Refresh every 30 seconds

    return () => clearInterval(interval);
  }, [dispatch]);

  const activeStreams = streams.filter(
    (stream) => stream.stream_status === "active"
  );

  return (
    <Container size="xl" py="xl">
      <Stack spacing="lg">
        <Group position="apart">
          <Title order={2}>Live Cameras</Title>
          <Group>
            <Select
              label="Grid Layout"
              value={gridColumns.toString()}
              onChange={(value) => setGridColumns(Number(value))}
              data={[
                { value: "1", label: "1 Column" },
                { value: "2", label: "2 Columns" },
                { value: "3", label: "3 Columns" },
                { value: "4", label: "4 Columns" },
              ]}
            />
            <Button
              variant="light"
              onClick={() => dispatch(fetchStreams())}
              loading={loading}
            >
              Refresh
            </Button>
          </Group>
        </Group>

        {error && (
          <Text color="red" size="sm">
            Error: {error}
          </Text>
        )}

        {!loading && activeStreams.length === 0 && (
          <Text color="dimmed" align="center" mt="xl">
            No active streams found
          </Text>
        )}

        <StreamGrid streams={activeStreams} columns={gridColumns} />
      </Stack>
    </Container>
  );
}
