import { Radio, RadioGroup } from "@material-ui/core";
import FormControlLabel from "@material-ui/core/FormControlLabel";
import React from "react";
import { Controller, useFormContext, useWatch } from "react-hook-form";

import useStyles from "./styles";

const options = ["DISABLED", "LOCAL", "REMOTE"];

const WebhookTable = ({ isProcessing }) => {
  const classes = useStyles();
  const { control, watch } = useFormContext();
  const activeWebhooks = watch("activeWebhooks");
  const webhookTypes = Object.keys(activeWebhooks);

  return (
    <div>
      <div className={classes.row}>
        <p>Webhook Type</p>
        <p className={classes.center}>DISABLED</p>
        <p className={classes.center}>LOCAL</p>
        <p className={classes.center}>REMOTE</p>
      </div>

      {webhookTypes.map((webhookType) => (
        <Controller
          key={webhookType}
          name={`activeWebhooks.${webhookType}`}
          control={control}
          render={(props) => (
            <RadioGroup
              row
              key={webhookType}
              onChange={props.onChange}
              value={activeWebhooks[webhookType]}
              className={classes.row}
            >
              <>
                <p>{webhookType}</p>
                {options.map((option) => (
                  <FormControlLabel
                    value={option}
                    label={null}
                    key={option}
                    className={classes.center}
                    control={<Radio color="primary" disabled={isProcessing} />}
                  />
                ))}
              </>
            </RadioGroup>
          )}
        />
      ))}
    </div>
  );
};

export default WebhookTable;
