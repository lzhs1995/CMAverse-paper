-- 仅使用Word术语；读取对象列表后在本地计数，避免向文档集合发送count事件。
on inventory()
    tell application "Microsoft Word"
        set docs to (get every document)
        set wins to (get every window)
    end tell
    set outText to "WORD_INVENTORY_V2" & tab & (count of docs) & tab & (count of wins) & linefeed
    repeat with itemRef in docs
        set docRef to contents of itemRef
        tell application "Microsoft Word"
            set p to (get posix full name of docRef)
            set s to (get saved of docRef)
        end tell
        if p is "" then error "DOCUMENT_PATH_UNKNOWN"
        if p contains tab or p contains linefeed or p contains return then error "DOCUMENT_PATH_UNSUPPORTED"
        set outText to outText & "DOC" & tab & p & tab & (s as text) & linefeed
    end repeat
    tell application "Microsoft Word"
        set finalDocs to (get every document)
        set finalWins to (get every window)
    end tell
    if (count of finalDocs) is not (count of docs) then error "DOCUMENTS_CHANGED"
    if (count of finalWins) is not (count of wins) then error "WINDOWS_CHANGED"
    return outText & "END"
end inventory
with timeout of 12 seconds
    return my inventory()
end timeout
