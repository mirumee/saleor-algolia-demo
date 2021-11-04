import { yupResolver } from "@hookform/resolvers/yup";
import { Card, CardContent } from "@material-ui/core";
import MuiAlert from "@material-ui/lab/Alert";
import { createApp } from "@saleor/app-bridge";
import { ConfirmButton } from "@saleor/macaw-ui";
import React, { useEffect, useState } from "react";
import { FormProvider, useForm } from "react-hook-form";

import Credentials from "../Credentials";
import useStyles from "../styles";
import WebhookConfiguration from "../WebhookConfiguration";
import { configSchema } from "./schema";

const app = createApp();
const root = document.getElementById("root");
const configDataUrl = root.getAttribute("data-configuration-url");
const webhookTypes = root.getAttribute("data-webhook-types").split(",");
const languagesList = JSON.parse(root.getAttribute("data-languages"));

export const ConfigurationForm = () => {
  const classes = useStyles();
  const [btnState, setBtnState] = useState("default");
  const [isProcessing, setProcessing] = useState(false);
  const [errored, setErrored] = useState(false);
  const [token, setToken] = useState(null);

  const { domain, token: defaultToken } = app.getState();

  const headers = {
    "content-type": "application/json",
    "x-saleor-token": token ? token : defaultToken,
    "x-saleor-domain": domain,
  };

  const formCtx = useForm({
    resolver: yupResolver(configSchema),
    defaultValues: {
      activeWebhooks: [],
      algoliaApiKey: "",
      algoliaAppId: "",
      chosenLanguages: [],
      saleorDomain: "",
      transformationServiceApiKey: "",
      transformationServiceUrl: "",
    },
  });

  const fetchAndSet = async () => {
    setProcessing(true);

    const response = await fetch(configDataUrl, {
      headers,
      method: "GET",
    });

    if (!response.ok) {
      setErrored(true);
      return;
    }

    const data = await response.json();

    const activeWebhooks = webhookTypes.reduce(
      (webhooksConfig, webhookType) => {
        const { transformation_type } =
          data.active_webhooks.find(
            (webhook) => webhook.type === webhookType
          ) || {};

        webhooksConfig[webhookType] = transformation_type ?? "DISABLED";

        return webhooksConfig;
      },
      {}
    );

    formCtx.reset({
      activeWebhooks: activeWebhooks,
      algoliaApiKey: data.algolia_api_key,
      algoliaAppId: data.algolia_app_id,
      chosenLanguages: data.languages_list,
      saleorDomain: domain,
      transformationServiceApiKey: data.transformation_service?.api_key,
      transformationServiceUrl: data.transformation_service?.url,
    });

    setProcessing(false);
  };

  const onSubmit = async ({
    activeWebhooks,
    algoliaApiKey,
    algoliaAppId,
    transformationServiceUrl,
    transformationServiceApiKey,
    chosenLanguages = [],
  }) => {
    setBtnState("loading");
    setProcessing(true);

    const transformedActiveWebhooks = Object.keys(activeWebhooks).reduce(
      (webhooks, webhookType) => {
        const transformationType = activeWebhooks[webhookType];
        if (!transformationType || transformationType === "DISABLED") {
          return webhooks;
        }

        webhooks.push({
          type: webhookType,
          transformation_type: transformationType,
        });

        return webhooks;
      },
      []
    );

    try {
      const response = await fetch(configDataUrl, {
        headers,
        body: JSON.stringify({
          algolia_api_key: algoliaApiKey,
          algolia_app_id: algoliaAppId,
          languages_list: chosenLanguages,
          active_webhooks: transformedActiveWebhooks,
          transformation_service: {
            url: transformationServiceUrl,
            api_key: transformationServiceApiKey,
          },
        }),
        method: "POST",
      });

      setBtnState(response.ok ? "success" : "error");
    } catch (err) {
      setBtnState("error");
    }

    setProcessing(false);
  };

  const subscribe = () => {
    app.subscribe("handshake", ({ token }) => {
      setToken(token);
      headers["x-saleor-token"] = token;
      fetchAndSet();
    });
  };

  useEffect(() => {
    subscribe();

    return () => app.unsubscribeAll("handshake");
  }, []);

  return (
    <FormProvider {...formCtx}>
      <form onSubmit={formCtx.handleSubmit(onSubmit)}>
        <Card>
          {errored && (
            <CardContent>
              <MuiAlert severity="error">
                An error occurred while fetching the configuration. Please try
                again later.
              </MuiAlert>
            </CardContent>
          )}

          <Credentials isProcessing={isProcessing} />
          <WebhookConfiguration
            isProcessing={isProcessing}
            languagesList={languagesList}
          />
          <CardContent>
            <div className={classes.actionContainer}>
              <ConfirmButton
                variant="contained"
                color="primary"
                type="submit"
                disabled={isProcessing}
                transitionState={btnState}
                errorlabel="Error"
                labels={{ confirm: "Confirm", error: "Error" }}
              >
                Save
              </ConfirmButton>
            </div>
          </CardContent>
        </Card>
      </form>
    </FormProvider>
  );
};
