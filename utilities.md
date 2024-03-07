## Utilities
Common utilities & workflows for various applications.

#### Converting notes from Todoist app
Use **Find & Replace** on your text editor, and search with the following regex:

```
(^|\n)([a-zA-Z0-9])
```

Replace it with:

```
$1- $2
```
Equivalent `sed` command, use **`-i ''`** to apply changes in the file:

```
sed -E "s/(^|\n)([a-zA-Z0-9])/\1- \2/g" file.txt
```