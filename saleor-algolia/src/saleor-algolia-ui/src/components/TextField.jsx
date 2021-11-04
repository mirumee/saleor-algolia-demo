import { IconButton, InputAdornment, TextField } from "@material-ui/core";
import Visibility from "@material-ui/icons/Visibility";
import VisibilityOff from "@material-ui/icons/VisibilityOff";
import React, { useState } from "react";
import { Controller, useFormContext } from "react-hook-form";

const CustomTextField = ({ label, name, toggleable, disabled }) => {
  const { control, errors } = useFormContext();
  const [showContent, setShowContent] = useState(!toggleable);

  const inputProps = {
    endAdornment: (
      <InputAdornment position="end">
        <IconButton
          onClick={() =>
            disabled ? undefined : setShowContent((state) => !state)
          }
          edge="end"
        >
          {showContent ? (
            <Visibility color={disabled ? "disabled" : "primary"} />
          ) : (
            <VisibilityOff color={disabled ? "disabled" : "primary"} />
          )}
        </IconButton>
      </InputAdornment>
    ),
  };

  return (
    <Controller
      name={name}
      control={control}
      render={(props) => (
        <TextField
          fullWidth
          value={props.value}
          disabled={disabled}
          error={!!errors[name]}
          helperText={errors[name]?.message}
          label={label}
          onChange={props.onChange}
          type={showContent ? "text" : "password"}
          InputProps={toggleable ? inputProps : undefined}
          {...props}
        />
      )}
    />
  );
};

export default CustomTextField;
