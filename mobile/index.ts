// index.ts: the Expo entry point. It registers App and nothing else.
// Everything the screen does lives in App.tsx and src/; this file must stay one line of work.
import { registerRootComponent } from "expo";

import App from "./App";

registerRootComponent(App);
