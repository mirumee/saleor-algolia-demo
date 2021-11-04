import makeStyles from "@material-ui/core/styles/makeStyles";

const useStyles = makeStyles((theme) => ({
  actionContainer: {
    display: "flex",
    justifyContent: "end",
  },
  flex: {
    flex: 1,
  },
  root: {
    display: "grid",
    gridTemplateColumns: "1fr",
  },
  spacer: {
    marginTop: theme.spacing(3),
  },
  formControl: {
    margin: theme.spacing(1),
    minWidth: 200,
  },
  chips: {
    display: "flex",
    flexWrap: "wrap",
  },
  chip: {
    margin: 2,
  },
  row: {
    display: "grid",
    gridTemplateColumns: "1fr 200px 200px 200px",
    borderBottom: "1px solid #eee",
  },
  center: {
    textAlign: "center",
    display: "flex",
    justifyContent: "center",
    margin: 0,
    alignItems: "center",
  },
}));

export default useStyles;
