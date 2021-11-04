import {
  CardContent,
  CardHeader,
  Chip,
  FormControl,
  InputLabel,
  MenuItem,
  OutlinedInput,
  Select,
  Typography,
} from "@material-ui/core";
import React from "react";
import { Controller, useFormContext } from "react-hook-form";

import useStyles from "./styles";
import TextField from "./TextField";
import WebhookTable from "./WebhookTable";

const Credentials = ({ isProcessing, languagesList }) => {
  const { control, watch } = useFormContext();
  const classes = useStyles({});
  const chosenLanguages = watch("chosenLanguages");

  const ITEM_HEIGHT = 48;
  const ITEM_PADDING_TOP = 8;
  const MenuProps = {
    PaperProps: {
      style: {
        maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
        width: 250,
      },
    },
  };

  const languagesOptions = React.useMemo(
    () =>
      languagesList.map(({ code, language }) => (
        <MenuItem key={code} value={code}>
          {language}
        </MenuItem>
      )),
    [languagesList]
  );

  return (
    <div className={classes.root}>
      <CardHeader title="Transformator Service Configuration" />

      <CardContent>
        <Typography variant="subtitle1" color="textSecondary">
          Remote Transformation Service
        </Typography>
        <Typography variant="body2" color="textSecondary" component="p">
          The following transformation service settings are only required when{" "}
          <b>REMOTE</b> transformation is chosen bellow
        </Typography>
        <div className={classes.spacer} />
        <TextField
          disabled={isProcessing}
          label="Transformation Service URL"
          name="transformationServiceUrl"
        />
        <div className={classes.spacer} />
        <TextField
          toggleable
          disabled={isProcessing}
          label="Transformation Service API Key"
          name="transformationServiceApiKey"
        />
      </CardContent>
      <CardHeader title="Webhook Configuration" />
      <CardContent>
        <FormControl
          variant="outlined"
          className={classes.formControl}
          disabled={isProcessing}
          fullWidth
        >
          <InputLabel>Languages</InputLabel>
          <Controller
            name="chosenLanguages"
            control={control}
            render={(props) => (
              <Select
                multiple
                value={chosenLanguages}
                onChange={props.onChange}
                input={<OutlinedInput label="Selected languages" />}
                MenuProps={MenuProps}
                renderValue={(selected) => (
                  <div className={classes.chips}>
                    {selected.map((value) => (
                      <Chip
                        key={value}
                        label={value}
                        className={classes.chip}
                      />
                    ))}
                  </div>
                )}
              >
                {languagesOptions}
              </Select>
            )}
          />
        </FormControl>

        <WebhookTable isProcessing={isProcessing} />
      </CardContent>
    </div>
  );
};

export default Credentials;
