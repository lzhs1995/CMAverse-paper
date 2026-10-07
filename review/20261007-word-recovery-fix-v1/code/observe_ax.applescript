-- 只读窗口归属；附属sheet归属于直接父窗口，原样保留，不枚举文件列表。
on cleanText(v)
    set v to v as text
    if v contains tab or v contains linefeed or v contains return then error "UNSUPPORTED_AX_TEXT"
    return v
end cleanText
on collectTexts(elem, appName, idx, depth)
    if depth > 12 then error "AX_DEPTH_LIMIT"
    tell application "System Events"
        set rr to role of elem
        if rr is "AXSheet" then
            if depth is not 1 then error "UNSUPPORTED_NESTED_SHEET"
            return "SHEET" & tab & appName & tab & idx & tab & "AXSheet" & linefeed
        end if
        set output to ""
        if rr is "AXStaticText" then
            set output to "TEXT" & tab & appName & tab & idx & tab & my cleanText(value of elem) & linefeed
        end if
        set children to UI elements of elem
        if (count of children) > 100 then error "AX_CHILD_LIMIT"
        repeat with child in children
            set output to output & my collectTexts(contents of child, appName, idx, depth + 1)
        end repeat
        return output
    end tell
end collectTexts
with timeout of 12 seconds
    set outText to "WORD_AX_V3" & linefeed
    tell application "System Events"
        if not (exists application process "Microsoft Word") then error "WORD_PROCESS_NOT_RUNNING"
        set outText to outText & "WORD_PROCESS" & tab & "true" & linefeed
        repeat with appName in {"Microsoft Word", "Zotero"}
            if exists application process (contents of appName) then
                tell application process (contents of appName)
                    set idx to 0
                    repeat with w in windows
                        set idx to idx + 1
                        set nm to my cleanText(name of w)
                        set rl to my cleanText(value of attribute "AXRole" of w)
                        set sr to my cleanText(value of attribute "AXSubrole" of w)
                        set md to (value of attribute "AXModal" of w) as text
                        set sh to count of sheets of w
                        set outText to outText & "WIN" & tab & (contents of appName) & tab & idx & tab & nm & tab & rl & tab & sr & tab & md & tab & sh & linefeed
                        if md is "true" or sr is not "AXStandardWindow" or sh > 0 then
                            set outText to outText & my collectTexts(contents of w, contents of appName, idx, 0)
                        end if
                    end repeat
                end tell
            end if
        end repeat
    end tell
    return outText & "END"
end timeout
