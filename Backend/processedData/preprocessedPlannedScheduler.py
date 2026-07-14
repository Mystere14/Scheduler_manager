import pandas as pd
from io import BytesIO
from routes.lesson import deleteTrueLesson
from processedData.sessionName import sessionName

def preprocessSchedulerPlanned( plannedScheduler : bytes):

    df = pd.read_csv(BytesIO(plannedScheduler), sep=";")

    df = df[df["volume"] != 0]

    hetuLine = df[df["code_ens"] == "HETU"]

    hetuLine = hetuLine[["code_res_sae", "semaine", "type_ens", "volume"]].rename(columns={"volume": "volume_hetu"})

    df = df.merge(
    hetuLine,
    on=["code_res_sae", "semaine", "type_ens"],
    how="left"
    )

    df["format"] = 1.0
    df.loc[df["volume_hetu"] % 1.5 == 0, "format"] = 1.5
    df.loc[df["volume_hetu"] % 2 == 0, "format"] = 2

    df = df[df["code_ens"] != "HETU"]

    df["line"] = (df["volume"] / df["format"]).astype(int)

    df["volume"] = df["volume"]/df["line"] 

    df["code_res_sae"] = df["code_res_sae"].str.strip()
    df["code_res_sae"] = df["code_res_sae"].str.slice(0, 3) + "-" +df["code_res_sae"].str.slice(5, 6) + "-" +df["code_res_sae"].str.slice(4, 8)
    df["code_res_sae"] = df["code_res_sae"].map(sessionName)

    df = df.loc[df.index.repeat(df["line"])]

    df = df.drop(columns=["volume_hetu","line","format"])

    deleteTrueLesson()

    df.rename(columns={"code_ens": "codeEns", "code_res_sae": "codeResSae", "semaine": "week", "type_ens": "typeEns"}, inplace=True)

    return df.to_dict(orient="records")
