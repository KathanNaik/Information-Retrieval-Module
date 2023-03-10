import tkinter as tk

queryList = []


def getValue():
    userInput = entry.get()
    entry.delete("0", tk.END)

    value = userInput
    # print(value)
    queryList.append(value)
    # print(queryList)

    printResult()


def printResult():
    title = tk.Label(root, text=f'Your Results will be in file:', pady=10, bg='#ffbf00').pack()
    link = tk.Label(root, text="searchResult.txt", font=('Helveticabold', 15), fg="blue")
    link.pack()


def returnLastQuery():
    return queryList[-1]


def saveQueryListToFile():
    with open('log.txt', 'w') as txt:
        txt.write("\n".join(queryList))


def readQueryListFromFile():
    with open('log.txt') as txt:
        global queryList
        queryList = txt.read().split('\n')


readQueryListFromFile()
root = tk.Tk()

root.title("Query")
root.geometry('400x300')
root['bg'] = '#ffbf00'

tk.Label(root, text=f'Enter Your Query Here!', pady=10, bg='#ffbf00').pack()

entry = tk.Entry(root, width=50, textvariable=tk.StringVar())
entry.pack()

tk.Label(root, text=f'', pady=0, bg='#ffbf00').pack()

button = tk.Button(root, text="Enter", command=getValue)
button.pack()

tk.Label(root, text=f'Your Previous Queries:', pady=10, bg='#ffbf00').pack()
tk.Label(root, text=f'{queryList[len(queryList) - 1]}', pady=2, bg='#ffbf00').pack()
tk.Label(root, text=f'{queryList[len(queryList) - 2]}', pady=2, bg='#ffbf00').pack()
tk.Label(root, text=f'{queryList[len(queryList) - 3]}', pady=2, bg='#ffbf00').pack()

root.mainloop()

