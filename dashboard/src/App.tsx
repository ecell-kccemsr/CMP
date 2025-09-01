import { MantineProvider } from "@mantine/core";
import { CameraView } from "./pages/CameraView";

function App() {
  return (
    <MantineProvider
      withGlobalStyles
      withNormalizeCSS
      theme={{
        colorScheme: "dark",
        primaryColor: "blue",
      }}
    >
      <CameraView />
    </MantineProvider>
  );
}

export default App;
