# PLAN.md — DaVinci Resolve Wrapper API — Implementation Status

**Based on:** DaVinci Resolve Scripting API v20.3 (October 2025)
**Goal:** Expose every method as an HTTP endpoint

---

## 🔜 TODO — Remaining Work (Priority Order)

### High Priority (needed for SB4 render pipeline)
1. **`GetRenderJobStatus()` returns 0%** — Investigate DaVinci's actual return format. Try `GetRenderJobList()` to get integer IDs, then use those for status calls
2. **TimelineItem operations** — `GetItemsInTrack()`, `GetTrackCount()`, `SetCurrentTimeline()` index-based, `DeleteTimelines()` by name
3. **Batch media import** — Add endpoint for batched imports (20 files at a time) to avoid crashes
4. **File-size polling for render progress** — Implement progress tracking via output file size

### Medium Priority (useful for automation)
5. **`AppendToTimeline()`** — Add clips directly to timeline without manual linking
6. **Timeline item retime/trim** — `Retime()`, `SetSpeed()`, `SetDuration()`, `SetStart()`
7. **Export project as `.drp`** — `POST /api/projects/export` needs testing
8. **Set timeline name** — `Timeline.SetName()`
9. **Get timeline range** — `GetStartFrame()`, `GetEndFrame()`
10. **Render preset save/delete** — `POST /api/render/preset/save`, `/delete`
11. **Timeline markers** — `POST /api/timeline/{index}/markers/add` needs testing

### Low Priority (nice to have)
12. **TimelineItem (76+ methods)** — retime curves, keyframes, transforms, crop, compositing, Fusion, takes, etc.
13. **Fusion node graph** — add/delete/connect nodes (needs Fusion page context)
14. **Gallery/stills** — album management, still export
15. **ColorGroup management** — `GetColorGroupsList()`, `AddColorGroup()`, `DeleteColorGroup()`
16. **Fairlight** — `InsertAudioToCurrentTrackAtPlayhead()`, `ApplyFairlightPresetToCurrentTimeline()`
17. **Cloud projects** — `CreateCloudProject()`, `LoadCloudProject()`, etc.
18. **Burn-in presets** — `LoadBurnInPreset()`
19. **Frame export as still** — `ExportCurrentFrameAsStill()`
20. **Keyframe mode** — `GetKeyframeMode()`, `SetKeyframeMode()`
21. **LUT refresh** — `RefreshLUTList()`
22. **Clip versions** — `AddVersion()`, `GetVersions()`, `DeleteVersion()`

### Documentation Only
- Add more endpoint examples to `davinci-api-test-results.md`
- Write usage guide for batch media import

---

## Test Status
- **Fully tested:** Most core endpoints — see `notes/davinci-api-test-results.md`
- **Not tested:** Project export/archive/restore, render preset save/delete, specific clip metadata endpoints, timeline markers add, layout preset update/delete, render preset import/export
- **Not implemented:** TimelineItem (76+ methods), Gallery, Fusion/Graph, ColorGroup, various Project settings methods

### Untested Endpoints (implemented):
- `POST /api/projects/export`, `/archive`, `/restore`
- `POST /api/projects/folders/create`, `/delete`
- `POST /api/resolve/render-preset/import`, `/export`
- `POST /api/resolve/layout-preset/update`, `/delete`
- `POST /api/resolve/quit`
- `POST /api/render/preset/save`, `/delete`
- `POST /api/render/job/delete` (specific job)
- `GET /api/render/quick-export-presets`
- `GET /api/timeline/{index}/fusion/node-graph` (needs Fusion page)
- `POST /api/timeline/{index}/markers/add`
- Various clip metadata endpoints: flags, color, markers, audio sync

---

## Known Issues

- **`GetRenderJobStatus()` returns null/Unknown**: DaVinci's `GetRenderJobStatus(jobId)` returns `None` for the status dict when called with the job ID returned by `AddRenderJob()`. The job ID from `AddRenderJob()` appears to be a UUID/string, but DaVinci internally uses integer IDs. Workaround: file-size polling on output file to track progress. (2026-04-01)
- **`GetRenderJobList()` keys are capitalised**: DaVinci returns `JobId` (capital I), `OutputPath`, `Status` — not lowercase. Wrapper now handles both cases. (2026-04-01)
- **Bulk media import crashes DaVinci**: Importing 200+ files via `AddItemListToMediaPool()` in one call causes DaVinci to freeze/crash. Import in batches of ~20 files. (2026-04-01)
- **`Proxy Media Path` causes offline clips**: Icepha's projects store proxy paths as `D:\GoodSync\...` which don't exist on Tackle's machine. DaVinci checks proxy path before File Path. Fix: copy proxy files to match the expected paths. (2026-04-01)

---

## API Classes & Coverage Status

| Class | Methods | Status | HTTP Group |
|-------|---------|--------|------------|
| Resolve | 21 | ✅ Done | `/api/resolve` |
| ProjectManager | 25 | ✅ Done | `/api/projects` |
| Project | 42 | ✅ Done | `/api/projects`, `/api/render` |
| MediaStorage | 9 | ✅ Done | `/api/media` |
| MediaPool | 27 | ✅ Done | `/api/media` |
| Folder | 8 | ✅ Done | `/api/projects` |
| MediaPoolItem | 32+ | ✅ Done | `/api/media` |
| Timeline | 56 | ✅ Done | `/api/timeline` |
| TimelineItem | 76+ | 🔜 Future | `/api/timeline` |
| Gallery | 8 | 🔜 Future | `/api/gallery` |
| GalleryStillAlbum | 6 | 🔜 Future | `/api/gallery` |
| Graph | 22 | 🔜 Future | `/api/fusion` |
| ColorGroup | 10 | 🔜 Future | `/api/timeline` |

---

## Resolve — Implementation Status

| Method | Status | Endpoint |
|--------|--------|----------|
| `GetMediaStorage()` | ✅ Done | Via media endpoints |
| `GetProjectManager()` | ✅ Done | Via projects endpoints |
| `OpenPage(pageName)` | ✅ Done | `POST /api/resolve/open-page` |
| `GetCurrentPage()` | ✅ Done | `GET /api/resolve/current-page` |
| `GetProductName()` | ✅ Done | `GET /api/resolve/health` |
| `GetVersion()` | ✅ Done | `GET /api/resolve/health` |
| `GetVersionString()` | ✅ Done | `GET /api/resolve/health` |
| `LoadLayoutPreset(presetName)` | ✅ Done | `POST /api/resolve/layout-preset/load` |
| `UpdateLayoutPreset(presetName)` | ✅ Done | `POST /api/resolve/layout-preset/update` |
| `ExportLayoutPreset(presetName, filePath)` | ✅ Done | `POST /api/resolve/layout-preset/export` |
| `SaveLayoutPreset(presetName)` | ✅ Done | `POST /api/resolve/layout-preset/save` |
| `DeleteLayoutPreset(presetName)` | ✅ Done | `POST /api/resolve/layout-preset/delete` |
| `ImportLayoutPreset(filePath, name)` | ✅ Done | `POST /api/resolve/layout-preset/import` |
| `GetKeyframeMode()` | 🔜 Future | — |
| `SetKeyframeMode(keyframeMode)` | 🔜 Future | — |
| `GetFairlightPresets()` | 🔜 Future | — |
| `ImportRenderPreset(presetPath)` | ✅ Done | `POST /api/resolve/render-preset/import` |
| `ExportRenderPreset(presetName, exportPath)` | ✅ Done | `POST /api/resolve/render-preset/export` |
| `Quit()` | ✅ Done | `POST /api/resolve/quit` |
| `Fusion()` | 🔜 Future | Via Fusion endpoints |

---

## ProjectManager — Implementation Status

| Method | Status | Endpoint |
|--------|--------|----------|
| `CreateProject(projectName, mediaLocationPath)` | ✅ Done | `POST /api/projects/create` |
| `DeleteProject(projectName)` | ✅ Done | `POST /api/projects/delete` |
| `LoadProject(projectName)` | ✅ Done | `POST /api/projects/load` |
| `GetCurrentProject()` | ✅ Done | `GET /api/projects/current` |
| `SaveProject()` | ✅ Done | `POST /api/projects/save` |
| `CloseProject(project)` | ✅ Done | `POST /api/projects/close` |
| `CreateFolder(folderName)` | ✅ Done | `POST /api/projects/folders/create` |
| `DeleteFolder(folderName)` | ✅ Done | `POST /api/projects/folders/delete` |
| `GetProjectListInCurrentFolder()` | ✅ Done | `GET /api/projects` |
| `GetFolderListInCurrentFolder()` | ✅ Done | `GET /api/projects/folders` |
| `GotoRootFolder()` | ✅ Done | `POST /api/projects/folders/navigate` |
| `GotoParentFolder()` | ✅ Done | `POST /api/projects/folders/navigate` |
| `GetCurrentFolder()` | ✅ Done | Via project endpoints |
| `OpenFolder(folderName)` | ✅ Done | `POST /api/projects/folders/navigate` |
| `ImportProject(filePath, projectName)` | ✅ Done | `POST /api/projects/import` |
| `ExportProject(name, filePath, withStillsAndLUTs)` | ✅ Done | `POST /api/projects/export` |
| `ArchiveProject(name, filePath, ...)` | ✅ Done | `POST /api/projects/archive` |
| `RestoreProject(filePath, projectName)` | ✅ Done | `POST /api/projects/restore` |
| `GetCurrentDatabase()` | ✅ Done | `GET /api/projects/database` |
| `GetDatabaseList()` | ✅ Done | `GET /api/projects/databases` |
| `SetCurrentDatabase({dbInfo})` | ✅ Done | `POST /api/projects/database/set` |
| `CreateCloudProject({cloudSettings})` | 🔜 Future | — |
| `LoadCloudProject({cloudSettings})` | 🔜 Future | — |
| `ImportCloudProject(filePath, {cloudSettings})` | 🔜 Future | — |
| `RestoreCloudProject(folderPath, {cloudSettings})` | 🔜 Future | — |

---

## Project — Implementation Status

| Method | Status | Endpoint |
|--------|--------|----------|
| `GetMediaPool()` | ✅ Done | Via media endpoints |
| `GetTimelineCount()` | ✅ Done | `GET /api/projects/current` |
| `GetTimelineByIndex(idx)` | ✅ Done | `GET /api/timeline/{index}/items` |
| `GetCurrentTimeline()` | ✅ Done | `GET /api/timeline/current` |
| `SetCurrentTimeline(timeline)` | ✅ Done | `POST /api/timeline/current/set` |
| `GetName()` | ✅ Done | `GET /api/projects/current` |
| `SetName(projectName)` | 🔜 Future | — |
| `GetPresetList()` | 🔜 Future | — |
| `SetPreset(presetName)` | 🔜 Future | — |
| `AddRenderJob()` | ✅ Done | `POST /api/render/job/add` |
| `DeleteRenderJob(jobId)` | ✅ Done | `POST /api/render/job/delete` |
| `DeleteAllRenderJobs()` | ✅ Done | `POST /api/render/jobs/clear` |
| `GetRenderJobList()` | ✅ Done | `GET /api/render/jobs` |
| `GetRenderPresetList()` | ✅ Done | `GET /api/render/presets` |
| `StartRendering(jobId1, ...)` | ✅ Done | `POST /api/render/start` |
| `StopRendering()` | ✅ Done | `POST /api/render/stop` |
| `IsRenderingInProgress()` | ✅ Done | `GET /api/render/status` |
| `LoadRenderPreset(presetName)` | ✅ Done | `POST /api/render/preset/load` |
| `SaveAsNewRenderPreset(presetName)` | ✅ Done | `POST /api/render/preset/save` |
| `DeleteRenderPreset(presetName)` | ✅ Done | `POST /api/render/preset/delete` |
| `SetRenderSettings({settings})` | ✅ Done | `POST /api/render/settings` |
| `GetRenderJobStatus(jobId)` | ✅ Done | `GET /api/render/status/{job_id}` |
| `GetQuickExportRenderPresets()` | ✅ Done | `GET /api/render/quick-export-presets` |
| `RenderWithQuickExport(preset_name, {params})` | ✅ Done | `POST /api/render/quick-export` |
| `GetRenderFormats()` | ✅ Done | `GET /api/render/formats` |
| `GetRenderCodecs(renderFormat)` | ✅ Done | `GET /api/render/codecs` |
| `GetCurrentRenderFormatAndCodec()` | ✅ Done | `GET /api/render/settings` |
| `SetCurrentRenderFormatAndCodec(format, codec)` | ✅ Done | `POST /api/render/format-set` |
| `GetCurrentRenderMode()` | ✅ Done | `GET /api/render/render-mode` |
| `SetCurrentRenderMode(renderMode)` | ✅ Done | `POST /api/render/render-mode` |
| `GetRenderResolutions(format, codec)` | ✅ Done | `GET /api/render/resolutions` |
| `GetSetting(settingName)` | 🔜 Future | — |
| `SetSetting(settingName, settingValue)` | 🔜 Future | — |
| `GetUniqueId()` | 🔜 Future | — |
| `RefreshLUTList()` | 🔜 Future | — |
| `InsertAudioToCurrentTrackAtPlayhead(...)` | 🔜 Future | — |
| `LoadBurnInPreset(presetName)` | 🔜 Future | — |
| `ExportCurrentFrameAsStill(filePath)` | 🔜 Future | — |
| `GetColorGroupsList()` | 🔜 Future | — |
| `AddColorGroup(groupName)` | 🔜 Future | — |
| `DeleteColorGroup(colorGroup)` | 🔜 Future | — |
| `ApplyFairlightPresetToCurrentTimeline(name)` | 🔜 Future | — |
| `GetGallery()` | 🔜 Future | — |

---

## MediaStorage — Implementation Status

| Method | Status | Endpoint |
|--------|--------|----------|
| `GetMountedVolumeList()` | ✅ Done | `GET /api/media/volumes` |
| `GetSubFolderList(folderPath)` | ✅ Done | `GET /api/media/subfolders` |
| `GetFileList(folderPath)` | ✅ Done | `GET /api/media/files` |
| `RevealInStorage(path)` | ✅ Done | `POST /api/media/reveal` |
| `AddItemListToMediaPool(item1, item2, ...)` | ✅ Done | `POST /api/media/import` |
| `AddClipMattesToMediaPool(item, [paths], stereoEye)` | 🔜 Future | — |
| `AddTimelineMattesToMediaPool([paths])` | 🔜 Future | — |

---

## MediaPool — Implementation Status

| Method | Status | Endpoint |
|--------|--------|----------|
| `GetRootFolder()` | ✅ Done | `GET /api/media/pool` |
| `AddSubFolder(folder, name)` | ✅ Done | `GET /api/media/folder/create` |
| `CreateEmptyTimeline(name)` | ✅ Done | `POST /api/timeline/create` |
| `AppendToTimeline(clip1, clip2, ...)` | 🔜 Future | — |
| `CreateTimelineFromClips(name, clips...)` | ✅ Done | `POST /api/timeline/create-from-clips` |
| `ImportTimelineFromFile(filePath, {options})` | ✅ Done | `POST /api/timeline/import-file` |
| `DeleteTimelines([timeline])` | ✅ Done | `POST /api/timeline/delete` |
| `GetCurrentFolder()` | ✅ Done | `GET /api/media/pool` |
| `SetCurrentFolder(Folder)` | 🔜 Future | — |
| `DeleteClips([clips])` | ✅ Done | `POST /api/media/clip/delete` |
| `DeleteFolders([folders])` | 🔜 Future | — |
| `MoveClips([clips], targetFolder)` | ✅ Done | `POST /api/media/clip/move` |
| `MoveFolders([folders], targetFolder)` | 🔜 Future | — |
| `RelinkClips([MediaPoolItem], folderPath)` | ✅ Done | `POST /api/media/relink` |
| `UnlinkClips([MediaPoolItem])` | ✅ Done | `POST /api/media/unlink` |
| `ImportMedia([items...])` | ✅ Done | `POST /api/media/import` |
| `ExportMetadata(fileName, [clips])` | 🔜 Future | — |
| `CreateStereoClip(left, right)` | 🔜 Future | — |
| `AutoSyncAudio([items], {settings})` | ✅ Done | `POST /api/media/clip/auto-sync-audio` |
| `GetSelectedClips()` | 🔜 Future | — |
| `SetSelectedClip(MediaPoolItem)` | 🔜 Future | — |
| `RefreshFolders()` | 🔜 Future | — |
| `ImportFolderFromFile(filePath, sourceClipsPath)` | 🔜 Future | — |
| `GetClipMatteList(MediaPoolItem)` | 🔜 Future | — |
| `GetTimelineMatteList(Folder)` | 🔜 Future | — |
| `DeleteClipMattes(MediaPoolItem, [paths])` | 🔜 Future | — |

---

## Folder — Implementation Status

| Method | Status | Endpoint |
|--------|--------|----------|
| `GetClipList()` | ✅ Done | `GET /api/media/clips` |
| `GetName()` | ✅ Done | `GET /api/media/pool` |
| `GetSubFolderList()` | ✅ Done | `GET /api/media/subfolders` |
| `GetUniqueId()` | 🔜 Future | — |
| `Export(filePath)` | 🔜 Future | — |
| `GetIsFolderStale()` | 🔜 Future | — |
| `TranscribeAudio()` | 🔜 Future | — |
| `ClearTranscription()` | 🔜 Future | — |

---

## MediaPoolItem — Implementation Status

| Method | Status | Endpoint |
|--------|--------|----------|
| `GetName()` | ✅ Done | `GET /api/media/clip/{id}` |
| `SetName(name)` | ✅ Done | `POST /api/media/clip/{id}/rename` |
| `GetMetadata(metadataType)` | ✅ Done | `GET /api/media/clip/{id}` |
| `SetMetadata(metadataType, value)` | ✅ Done | `POST /api/media/clip/{id}/metadata` |
| `GetMediaId()` | ✅ Done | Via clip endpoints |
| `AddMarker(frameId, color, name, note, duration, customData)` | ✅ Done | `POST /api/media/clip/{id}/markers/add` |
| `GetMarkers()` | ✅ Done | `GET /api/media/clip/{id}/markers` |
| `DeleteMarkersByColor(color)` | ✅ Done | `POST /api/media/clip/{id}/markers/delete-by-color` |
| `DeleteMarkerAtFrame(frameNum)` | ✅ Done | `POST /api/media/clip/{id}/markers/delete-at-frame` |
| `AddFlag(color)` | ✅ Done | `POST /api/media/clip/{id}/flags/add` |
| `GetFlagList()` | ✅ Done | `GET /api/media/clip/{id}/flags` |
| `ClearFlags(color)` | ✅ Done | `POST /api/media/clip/{id}/flags/clear` |
| `GetClipColor()` | ✅ Done | `GET /api/media/clip/{id}` |
| `SetClipColor(colorName)` | ✅ Done | `POST /api/media/clip/{id}/color` |
| `ClearClipColor()` | ✅ Done | `POST /api/media/clip/{id}/clear-color` |
| `GetClipProperty(propertyName)` | 🔜 Future | — |
| `SetClipProperty(propertyName, propertyValue)` | 🔜 Future | — |
| `GetLinkedTimelineItems(trackType)` | 🔜 Future | — |
| `AddVersion({versionInfo})` | 🔜 Future | — |
| `DeleteVersion(versionIndex)` | 🔜 Future | — |
| `GetCurrentVersion()` | 🔜 Future | — |
| `GetVersions()` | 🔜 Future | — |
| `GetThirdPartyMetadata(metadataType)` | 🔜 Future | — |
| `SetThirdPartyMetadata(metadataType, value)` | 🔜 Future | — |
| `GetMarkerByCustomData(customData)` | 🔜 Future | — |
| `UpdateMarkerCustomData(frameId, customData)` | 🔜 Future | — |
| `GetMarkerCustomData(frameId)` | 🔜 Future | — |
| `DeleteMarkerByCustomData(customData)` | 🔜 Future | — |

---

## Timeline (Phase 2) — Implementation Status

| Method | Status | Endpoint |
|--------|--------|----------|
| `GetName()` | ✅ Done | Via timeline list |
| `SetName()` | 🔜 Future | — |
| `GetStartFrame()` | 🔜 Future | — |
| `GetEndFrame()` | 🔜 Future | — |
| `GetTrackCount()` | 🔜 Future | — |
| `GetItemsInTrack()` | 🔜 Future | — |
| `AddTrack()` | 🔜 Future | — |
| `DeleteTrack()` | 🔜 Future | — |
| `AddMarker()` | ✅ Done | `POST /api/timeline/{index}/markers/add` |
| `GetMarkers()` | ✅ Done | `GET /api/timeline/{index}/markers` |
| `DeleteMarkersByColor()` | 🔜 Future | — |
| `Export(presetName, exportPath)` | 🔜 Future | — |
| `ImportOTIO()` | 🔜 Future | — |
| `ExportOTIO()` | 🔜 Future | — |
| `AddGenerator()` | 🔜 Future | — |
| `GetGenerators()` | 🔜 Future | — |
| `AddTitle()` | 🔜 Future | — |
| `GetTitles()` | 🔜 Future | — |
| `GrabStill()` | 🔜 Future | — |
| `GrabStillAlbum()` | 🔜 Future | — |
| `FusionCopyNodeGraph()` | 🔜 Future | — |
| `FusionAsyncOpenPageGraph()` | 🔜 Future | — |
| `SetTrackLoudness()` | 🔜 Future | — |
| `GetTrackLoudness()` | 🔜 Future | — |
| `SetStereoMode()` | 🔜 Future | — |
| `GetStereoMode()` | 🔜 Future | — |
| `SetCurrent()` | ✅ Done | `POST /api/timeline/current/set` |
| `SetPlayhead()` | 🔜 Future | — |
| `GetCurrentTimecode()` | 🔜 Future | — |
| `GetCurrentVideoItem()` | 🔜 Future | — |

---

## TimelineItem (Phase 2) — Not Yet Implemented

All 76+ TimelineItem methods (retime, transform, crop, composite, audio, keyframes, fusion, color, takes, subtitle) are **🔜 Future**.

---

## Fusion / Graph — Not Yet Implemented

| Method | Status |
|--------|--------|
| `Fusion().AddNode(comp, node)` | 🔜 Future |
| `Fusion().GetNodeGraph(comp)` | ✅ Done | `GET /api/timeline/fusion/node-graph` |
| `Fusion().SetActiveNode(comp, node)` | 🔜 Future |
| `Fusion().AddTool(comp, node)` | 🔜 Future |
| `Fusion().DeleteTool(comp, node)` | 🔜 Future |
| Plus 17 more Fusion operations | 🔜 Future |

---

## Gallery — Not Yet Implemented

All Gallery and GalleryStillAlbum methods are **🔜 Future**.

---

## Future Enhancements

- Timeline item-level operations (retime, transform, keyframes)
- Fusion node manipulation (add, delete, connect nodes)
- Gallery/still albums
- Color group management
- Cloud projects
- Burn-in presets
- Audio transcription
- Keyframe mode operations
- Fairlight presets
- Import/export folder as DRB
