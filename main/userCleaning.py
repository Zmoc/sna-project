import cudf

userJsonPath = "Documents/1 - Projects/codingProjects/sna-project/data/rawYelpData/yelp_academic_dataset_user.json"
userCsvPath = (
    "Documents/1 - Projects/codingProjects/sna-project/data/cleanedData/user.csv"
)

df = cudf.read_json(userJsonPath, engine="cudf", lines=True)[["user_id", "friends"]]
df["user_id"], uniqueElements = df["user_id"].factorize()
mapping = cudf.DataFrame({"element": uniqueElements, "id": range(len(uniqueElements))})
df["friends"] = df["friends"].str.split(",")
df = df.explode(column="friends")
df["friends"] = df["friends"].str.replace(" ", "").str.strip()

mapping = mapping.rename(columns={"element": "user_id", "id": "friends"})

df = df.merge(mapping, left_on=["friends"], right_on=["user_id"], how="inner")
df = df.rename(columns={"user_id_x": "userID", "friends_y": "friendID"})
df = df[["userID", "friendID"]]

df.to_csv(userCsvPath, chunksize=100000, index=False)
