import * as yup from "yup";

const requiredMsg = "This field is required";
const requiredTransformationServiceField =
  "This field is required when any of the webhooks is set to REMOTE mode";
const urlMsg = "Must be a valid URL";

export const configSchema = yup.object().shape({
  saleorDomain: yup.string().required(requiredMsg),
  algoliaAppId: yup.string().required(requiredMsg),
  algoliaApiKey: yup.string().required(requiredMsg),
  transformationServiceApiKey: yup.mixed().when("activeWebhooks", {
    is: (activeWebhooks) => Object.values(activeWebhooks).includes("REMOTE"),
    then: yup.string().required(requiredTransformationServiceField),
    otherwise: yup.string(),
  }),
  transformationServiceUrl: yup.mixed().when("activeWebhooks", {
    is: (activeWebhooks) => Object.values(activeWebhooks).includes("REMOTE"),
    then: yup.string().url(urlMsg).required(requiredTransformationServiceField),
    otherwise: yup.string().url(urlMsg),
  }),
  chosenLanguages: yup.array().of(yup.string()).required(requiredMsg),
  activeWebhooks: yup
    .object()
    .shape({
      type: yup.string(),
      transformation_type: yup.string(),
    })
    .required(requiredMsg),
});
