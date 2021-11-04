import { ThemeProvider } from "@saleor/macaw-ui";
import React from "react";
import ReactDOM from "react-dom";

import App from "./App";

ReactDOM.render(
  <ThemeProvider>
    <App />
  </ThemeProvider>,
  document.getElementById("root")
);
