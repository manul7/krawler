# Task description
- implement recursive web-crawler of the site.
- crawler is a command-line tool that accept starting URL and destination directory
- crawler download the initial URL and look to links inside the original document (recursively)
- crawler does not walk to link outside initial url (if starting link is https://start.url/abc, then it goes to https://start.url/abc/123 and https://start.url/abc/456, but skip https://another.domain/ and https://start.url/def)
- crawler should correctly process Ctrl+C hotkey
- crawler should be parallel
- crawler should support continue to load if the destination directory already has loaded data (if we cancel the download and then continue).

# Timeframe for the task
4 hours.

# Note
In general, it's very similar to "wget --mirror" (with few extra options).
Does not necessary to implement all listed above, just do some (more important from your point of view) part, but take to account to do it in the way where every listed above is possible to add by extending your program (without re-writing from scratch)".
