import { CardContent, CardHeader } from "@material-ui/core";
import React from "react";

import useStyles from "./styles";
import TextField from "./TextField";

const ALGOLIA_CREDENTIALS = [
  { label: "Algolia Application ID", name: "algoliaAppId", toggleable: false },
  { label: "Algolia Admin API Key", name: "algoliaApiKey", toggleable: true },
];

const Credentials = ({ isProcessing }) => {
  const classes = useStyles();

  return (
    <div className={classes.root}>
      <CardHeader title="Algolia Credentials" />
      <CardContent>
        <TextField disabled label="Saleor Domain" name="saleorDomain" />
        <div className={classes.spacer} />

        {ALGOLIA_CREDENTIALS.map(({ label, name, toggleable }) => (
          <React.Fragment key={label}>
            <TextField
              label={label}
              name={name}
              disabled={isProcessing}
              toggleable={toggleable}
            />
            <div className={classes.spacer} />
          </React.Fragment>
        ))}
      </CardContent>
    </div>
  );
};

export default Credentials;
