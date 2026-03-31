# PLAN.md — DaVinci Wrapper API — API Coverage Plan

**Based on:** DaVinci Resolve Scripting API v20.3 (October 2025)
**Total API methods:** 324 across 13 object classes
**Goal:** Expose every method as an HTTP endpoint

---

## API Classes & Coverage Status

| Class | Methods | Status | HTTP Group |
|-------|---------|--------|------------|
| Resolve | 21 | ✅ To implement | `/api/resolve` |
| ProjectManager | 25 | ✅ To implement | `/api/projects` |
| Project | 42 | ✅ To implement | `/api/projects`, `/api/render` |
| MediaStorage | 9 | ✅ To implement | `/api/media` |
| MediaPool | 27 | ✅ To implement | `/api/media` |
| Folder | 8 | ✅ To implement | `/api/media` |
| MediaPoolItem | 32+ | ✅ To implement | `/api/media` |
| Timeline | 56 | ✅ To implement | `/api/timeline` |
| TimelineItem | 76+ | ✅ To implement | `/api/timeline` |
| Gallery | 8 | 🔜 Future | `/api/gallery` |
| GalleryStillAlbum | 6 | 🔜 Future | `/api/gallery` |
| Graph | 22 | 🔜 Future | `/api/fusion` |
| ColorGroup | 10 | 🔜 Future | `/api/timeline` |

---

## Phase 1 — Core Pipeline (2026-03-25)

Essential methods for the archive → import → relink → render pipeline.

### Resolve (21 methods)
| Method | Description | Priority |
|--------|-------------|----------|
| `Fusion()` | Returns Fusion object | 🔜 Phase 2 |
| `GetMediaStorage()` | Media storage object | ✅ Phase 1 |
| `GetProjectManager()` | Project manager | ✅ Phase 1 |
| `OpenPage(pageName)` | Switch page (media/cut/edit/fusion/color/fairlight/deliver) | ✅ Phase 1 |
| `GetCurrentPage()` | Current page name | ✅ Phase 1 |
| `GetProductName()` | Product name string | ✅ Phase 1 |
| `GetVersion()` | Version fields [major, minor, patch, build, suffix] | ✅ Phase 1 |
| `GetVersionString()` | Version string | ✅ Phase 1 |
| `LoadLayoutPreset(presetName)` | Load UI layout | ✅ Phase 1 |
| `UpdateLayoutPreset(presetName)` | Overwrite layout preset | 🔜 Phase 2 |
| `ExportLayoutPreset(presetName, filePath)` | Export layout to file | 🔜 Phase 2 |
| `DeleteLayoutPreset(presetName)` | Delete layout preset | 🔜 Phase 2 |
| `SaveLayoutPreset(presetName)` | Save current layout | 🔜 Phase 2 |
| `ImportLayoutPreset(filePath, name)` | Import layout | 🔜 Phase 2 |
| `Quit()` | Quit Resolve | ✅ Phase 1 |
| `ImportRenderPreset(presetPath)` | Import render preset | ✅ Phase 1 |
| `ExportRenderPreset(presetName, exportPath)` | Export render preset | ✅ Phase 1 |
| `ImportBurnInPreset(presetPath)` | Import burn-in preset | 🔜 Phase 2 |
| `ExportBurnInPreset(presetName, exportPath)` | Export burn-in preset | 🔜 Phase 2 |
| `GetKeyframeMode()` | Get keyframe mode | 🔜 Phase 2 |
| `SetKeyframeMode(keyframeMode)` | Set keyframe mode | 🔜 Phase 2 |
| `GetFairlightPresets()` | Fairlight presets list | 🔜 Phase 2 |

### ProjectManager (25 methods)
| Method | Description | Priority |
|--------|-------------|----------|
| `ArchiveProject(name, filePath, isArchiveSrcMedia, ...)` | Archive project with options | ✅ Phase 1 |
| `CreateProject(projectName, mediaLocationPath)` | Create new project | ✅ Phase 1 |
| `DeleteProject(projectName)` | Delete project | ✅ Phase 1 |
| `LoadProject(projectName)` | Load project by name | ✅ Phase 1 |
| `GetCurrentProject()` | Get currently loaded project | ✅ Phase 1 |
| `SaveProject()` | Save current project | ✅ Phase 1 |
| `CloseProject(project)` | Close project without saving | ✅ Phase 1 |
| `CreateFolder(folderName)` | Create project folder | ✅ Phase 1 |
| `DeleteFolder(folderName)` | Delete folder | ✅ Phase 1 |
| `GetProjectListInCurrentFolder()` | List projects in folder | ✅ Phase 1 |
| `GetFolderListInCurrentFolder()` | List subfolders | ✅ Phase 1 |
| `GotoRootFolder()` | Navigate to root | ✅ Phase 1 |
| `GotoParentFolder()` | Navigate to parent | ✅ Phase 1 |
| `GetCurrentFolder()` | Current folder name | ✅ Phase 1 |
| `OpenFolder(folderName)` | Open folder | ✅ Phase 1 |
| `ImportProject(filePath, projectName)` | Import .drp file | ✅ Phase 1 |
| `ExportProject(name, filePath, withStillsAndLUTs)` | Export to .drp | ✅ Phase 1 |
| `RestoreProject(filePath, projectName)` | Restore from archive | ✅ Phase 1 |
| `GetCurrentDatabase()` | Current DB info | ✅ Phase 1 |
| `GetDatabaseList()` | List all databases | ✅ Phase 1 |
| `SetCurrentDatabase({dbInfo})` | Switch database | ✅ Phase 1 |
| `CreateCloudProject({cloudSettings})` | Create cloud project | 🔜 Phase 2 |
| `LoadCloudProject({cloudSettings})` | Load cloud project | 🔜 Phase 2 |
| `ImportCloudProject(filePath, {cloudSettings})` | Import cloud project | 🔜 Phase 2 |
| `RestoreCloudProject(folderPath, {cloudSettings})` | Restore cloud project | 🔜 Phase 2 |

### Project (42 methods)
| Method | Description | Priority |
|--------|-------------|----------|
| `GetMediaPool()` | Media pool object | ✅ Phase 1 |
| `GetTimelineCount()` | Number of timelines | ✅ Phase 1 |
| `GetTimelineByIndex(idx)` | Get timeline by index | ✅ Phase 1 |
| `GetCurrentTimeline()` | Current timeline | ✅ Phase 1 |
| `SetCurrentTimeline(timeline)` | Set current timeline | ✅ Phase 1 |
| `GetGallery()` | Gallery object | 🔜 Phase 2 |
| `GetName()` | Project name | ✅ Phase 1 |
| `SetName(projectName)` | Rename project | ✅ Phase 1 |
| `GetPresetList()` | Project presets | ✅ Phase 1 |
| `SetPreset(presetName)` | Apply preset | ✅ Phase 1 |
| `AddRenderJob()` | Add job to queue | ✅ Phase 1 |
| `DeleteRenderJob(jobId)` | Delete render job | ✅ Phase 1 |
| `DeleteAllRenderJobs()` | Clear all jobs | ✅ Phase 1 |
| `GetRenderJobList()` | List render jobs | ✅ Phase 1 |
| `GetRenderPresetList()` | Render presets | ✅ Phase 1 |
| `StartRendering(jobId1, ...)` | Start rendering | ✅ Phase 1 |
| `StopRendering()` | Stop rendering | ✅ Phase 1 |
| `IsRenderingInProgress()` | Check if rendering | ✅ Phase 1 |
| `LoadRenderPreset(presetName)` | Load render preset | ✅ Phase 1 |
| `SaveAsNewRenderPreset(presetName)` | Save new preset | ✅ Phase 1 |
| `DeleteRenderPreset(presetName)` | Delete render preset | ✅ Phase 1 |
| `SetRenderSettings({settings})` | Set render settings | ✅ Phase 1 |
| `GetRenderJobStatus(jobId)` | Job status + progress | ✅ Phase 1 |
| `GetQuickExportRenderPresets()` | Quick export presets | ✅ Phase 1 |
| `RenderWithQuickExport(preset_name, {params})` | Quick export | ✅ Phase 1 |
| `GetSetting(settingName)` | Project setting | ✅ Phase 1 |
| `SetSetting(settingName, settingValue)` | Set project setting | ✅ Phase 1 |
| `GetRenderFormats()` | Render formats | ✅ Phase 1 |
| `GetRenderCodecs(renderFormat)` | Codecs for format | ✅ Phase 1 |
| `GetCurrentRenderFormatAndCodec()` | Current format/codec | ✅ Phase 1 |
| `SetCurrentRenderFormatAndCodec(format, codec)` | Set format/codec | ✅ Phase 1 |
| `GetCurrentRenderMode()` | Render mode (individual/single) | ✅ Phase 1 |
| `SetCurrentRenderMode(renderMode)` | Set render mode | ✅ Phase 1 |
| `GetRenderResolutions(format, codec)` | Available resolutions | ✅ Phase 1 |
| `RefreshLUTList()` | Refresh LUT list | 🔜 Phase 2 |
| `GetUniqueId()` | Project unique ID | ✅ Phase 1 |
| `InsertAudioToCurrentTrackAtPlayhead(...)` | Insert audio at playhead | 🔜 Phase 2 |
| `LoadBurnInPreset(presetName)` | Load burn-in preset | 🔜 Phase 2 |
| `ExportCurrentFrameAsStill(filePath)` | Export current frame | 🔜 Phase 2 |
| `GetColorGroupsList()` | Color groups | 🔜 Phase 2 |
| `AddColorGroup(groupName)` | Add color group | 🔜 Phase 2 |
| `DeleteColorGroup(colorGroup)` | Delete color group | 🔜 Phase 2 |
| `ApplyFairlightPresetToCurrentTimeline(name)` | Apply Fairlight preset | 🔜 Phase 2 |

### MediaStorage (9 methods)
| Method | Description | Priority |
|--------|-------------|----------|
| `GetMountedVolumeList()` | List mounted volumes | ✅ Phase 1 |
| `GetSubFolderList(folderPath)` | List subfolders | ✅ Phase 1 |
| `GetFileList(folderPath)` | List files in folder | ✅ Phase 1 |
| `RevealInStorage(path)` | Reveal in media storage | ✅ Phase 1 |
| `AddItemListToMediaPool(item1, item2, ...)` | Import to media pool | ✅ Phase 1 |
| `AddItemListToMediaPool([items...])` | Bulk import | ✅ Phase 1 |
| `AddItemListToMediaPool([{itemInfo}])` | Import with frame range | ✅ Phase 1 |
| `AddClipMattesToMediaPool(item, [paths], stereoEye)` | Add mattes | 🔜 Phase 2 |
| `AddTimelineMattesToMediaPool([paths])` | Add timeline mattes | 🔜 Phase 2 |

### MediaPool (27 methods)
| Method | Description | Priority |
|--------|-------------|----------|
| `GetRootFolder()` | Root media pool folder | ✅ Phase 1 |
| `AddSubFolder(folder, name)` | Add subfolder | ✅ Phase 1 |
| `RefreshFolders()` | Refresh folders (collab) | 🔜 Phase 2 |
| `CreateEmptyTimeline(name)` | Create empty timeline | ✅ Phase 1 |
| `AppendToTimeline(clip1, clip2, ...)` | Append clips to timeline | ✅ Phase 1 |
| `AppendToTimeline([clips])` | Bulk append | ✅ Phase 1 |
| `AppendToTimeline([{clipInfo}])` | Append with frame info | ✅ Phase 1 |
| `CreateTimelineFromClips(name, clips...)` | Create from clips | ✅ Phase 1 |
| `CreateTimelineFromClips(name, [clips])` | Bulk create | ✅ Phase 1 |
| `CreateTimelineFromClips(name, [{clipInfo}])` | Create with clip info | ✅ Phase 1 |
| `ImportTimelineFromFile(filePath, {options})` | Import AAF/EDL/XML/FCPXML/DRT/ADL/OTIO | ✅ Phase 1 |
| `DeleteTimelines([timeline])` | Delete timelines | ✅ Phase 1 |
| `GetCurrentFolder()` | Current folder | ✅ Phase 1 |
| `SetCurrentFolder(Folder)` | Set current folder | ✅ Phase 1 |
| `DeleteClips([clips])` | Delete clips | ✅ Phase 1 |
| `ImportFolderFromFile(filePath, sourceClipsPath)` | Import folder from DRB | 🔜 Phase 2 |
| `DeleteFolders([folders])` | Delete folders | ✅ Phase 1 |
| `MoveClips([clips], targetFolder)` | Move clips | ✅ Phase 1 |
| `MoveFolders([folders], targetFolder)` | Move folders | ✅ Phase 1 |
| `GetClipMatteList(MediaPoolItem)` | Get mattes for clip | 🔜 Phase 2 |
| `GetTimelineMatteList(Folder)` | Get timeline mattes | 🔜 Phase 2 |
| `DeleteClipMattes(MediaPoolItem, [paths])` | Delete mattes | 🔜 Phase 2 |
| **`RelinkClips([MediaPoolItem], folderPath)`** | **Relink media to new path** | ✅ Phase 1 |
| `UnlinkClips([MediaPoolItem])` | Unlink clips | 🔜 Phase 2 |
| `ImportMedia([items...])` | Import media | ✅ Phase 1 |
| `ImportMedia([{clipInfo}])` | Import with info | ✅ Phase 1 |
| `ExportMetadata(fileName, [clips])` | Export metadata CSV | 🔜 Phase 2 |
| `GetUniqueId()` | Media pool unique ID | ✅ Phase 1 |
| `CreateStereoClip(left, right)` | Create stereo clip | 🔜 Phase 2 |
| `AutoSyncAudio([items], {settings})` | Auto sync audio | 🔜 Phase 2 |
| `GetSelectedClips()` | Get selected clips | ✅ Phase 1 |
| `SetSelectedClip(MediaPoolItem)` | Set selected clip | ✅ Phase 1 |

### Folder (8 methods)
| Method | Description | Priority |
|--------|-------------|----------|
| `GetClipList()` | Get clips in folder | ✅ Phase 1 |
| `GetName()` | Folder name | ✅ Phase 1 |
| `GetSubFolderList()` | Subfolders | ✅ Phase 1 |
| `GetIsFolderStale()` | Check if stale (collab) | 🔜 Phase 2 |
| `GetUniqueId()` | Folder unique ID | ✅ Phase 1 |
| `Export(filePath)` | Export folder as DRB | 🔜 Phase 2 |
| `TranscribeAudio()` | Transcribe folder audio | 🔜 Phase 2 |
| `ClearTranscription()` | Clear transcription | 🔜 Phase 2 |

### MediaPoolItem (32+ methods)
| Method | Description | Priority |
|--------|-------------|----------|
| `GetName()` | Clip name | ✅ Phase 1 |
| `SetName(name)` | Rename clip | ✅ Phase 1 |
| `GetMetadata(metadataType)` | Get metadata | ✅ Phase 1 |
| `SetMetadata(metadataType, value)` | Set metadata | ✅ Phase 1 |
| `SetMetadata({metadata})` | Bulk set metadata | ✅ Phase 1 |
| `GetThirdPartyMetadata(metadataType)` | Third-party metadata | 🔜 Phase 2 |
| `SetThirdPartyMetadata(metadataType, value)` | Set third-party metadata | 🔜 Phase 2 |
| `SetThirdPartyMetadata({metadata})` | Bulk set third-party | 🔜 Phase 2 |
| `GetMediaId()` | Unique clip ID | ✅ Phase 1 |
| `AddMarker(frameId, color, name, note, duration, customData)` | Add marker | ✅ Phase 1 |
| `GetMarkers()` | Get all markers | ✅ Phase 1 |
| `GetMarkerByCustomData(customData)` | Find marker by custom data | 🔜 Phase 2 |
| `UpdateMarkerCustomData(frameId, customData)` | Update marker custom data | 🔜 Phase 2 |
| `GetMarkerCustomData(frameId)` | Get marker custom data | 🔜 Phase 2 |
| `DeleteMarkersByColor(color)` | Delete markers by color | ✅ Phase 1 |
| `DeleteMarkerAtFrame(frameNum)` | Delete marker at frame | ✅ Phase 1 |
| `DeleteMarkerByCustomData(customData)` | Delete marker by custom data | 🔜 Phase 2 |
| `AddFlag(color)` | Add flag | ✅ Phase 1 |
| `GetFlagList()` | Get all flags | ✅ Phase 1 |
| `ClearFlags(color)` | Clear flags | ✅ Phase 1 |
| `GetClipColor()` | Get clip color | ✅ Phase 1 |
| `SetClipColor(colorName)` | Set clip color | ✅ Phase 1 |
| `ClearClipColor()` | Clear clip color | ✅ Phase 1 |
| `GetClipProperty(propertyName)` | Get clip property | ✅ Phase 1 |
| `SetClipProperty(propertyName, propertyValue)` | Set clip property | ✅ Phase 1 |
| `SetClipProperty({properties})` | Bulk set properties | ✅ Phase 1 |
| `AddVersion({versionInfo})` | Add timeline item version | 🔜 Phase 2 |
| `DeleteVersion(versionIndex)` | Delete version | 🔜 Phase 2 |
| `GetCurrentVersion()` | Get current version | 🔜 Phase 2 |
| `GetVersions()` | Get all versions | 🔜 Phase 2 |
| `GetLinkedTimelineItems(trackType)` | Linked timeline items | 🔜 Phase 2 |

---

## Phase 2 — Timeline & Advanced (Future)

### Timeline (56 methods)
| Category | Methods |
|----------|---------|
| Name/Properties | `GetName`, `SetName`, `GetStartFrame`, `GetEndFrame`, `GetTrackCount` |
| Tracks | `GetItemsInTrack`, `AddTrack`, `DeleteTrack`, `TrackType` enum |
| Markers | `AddMarker`, `GetMarkers`, `DeleteMarkersByColor`, `UpdateMarkerCustomData` |
| Export | `Export(presetName, exportPath)`, `ImportOTIO`, `ExportOTIO` |
| Generators | `AddGenerator`, `GetGenerators` |
| Titles | `AddTitle`, `GetTitles` |
| Stills | `GrabStill`, `GrabStillAlbum` |
| Fusion | `FusionCopyNodeGraph`, `FusionAsyncOpenPageGraph` |
| Audio | `SetTrackLoudness`, `GetTrackLoudness` |
| Stereo | `SetStereoMode`, `GetStereoMode` |
| Misc | `SetCurrent`, `SetPlayhead`, `GetCurrentTimecode`, `GetCurrentVideoItem` |

### TimelineItem (76+ methods)
| Category | Methods |
|----------|---------|
| Properties | `GetName`, `GetDuration`, `GetEnd`, `GetStart`, `GetPlayhead`, `SetProperty` |
| Retime | `GetRetime`, `SetRetime`, `GetSpeed`, `SetSpeed` |
| Transform | `GetTransform`, `SetTransform` |
| Crop | `GetCrop`, `SetCrop` |
| Composite | `GetCompositeMode`, `SetCompositeMode`, `GetOpacity`, `SetOpacity` |
| Audio | `GetVolume`, `SetVolume`, `GetPan`, `SetPan`, `GetAudioEnabled` |
| Keyframes | `GetKeyframe*, Add*, Modify*, Delete*, SetKeyframe*` |
| Markers | `AddMarker`, `GetMarkers`, `DeleteMarkerAtFrame` |
| Fusion | `FusionAddNode`, `FusionGetComp` |
| Versions | `AddVersion`, `GetCurrentVersion`, `GetVersions`, `DeleteVersion` |
| Color | `SetLUT`, `GetLUT`, `SetCDL`, `ApplyGradeFromDRX` |
| Takes | `GetActiveTake`, `GetTakesCount`, `GetTakeByIndex` |
| Subtitle | `GetSubtitleTrackItems` |

### Fusion / Graph (22 methods)
| Method | Description |
|--------|-------------|
| `Fusion().AddNode(comp, node)` | Add node to comp |
| `Fusion().GetNodeGraph(comp)` | Get node graph |
| `Fusion().SetActiveNode(comp, node)` | Set active node |
| `Fusion().AddTool(comp, node)` | Add tool |
| `Fusion().DeleteTool(comp, node)` | Delete tool |
| Plus 17 more Fusion operations | LUTs, cache, undo grouping, render |

---

## Implementation Notes

### Platform Paths

The API paths differ by OS. The wrapper auto-detects the platform:

| OS | Script API Path | Library Path |
|----|----------------|--------------|
| Windows | `%PROGRAMDATA%\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting` | `C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll` |
| macOS | `/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting` | `DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so` |
| Linux | `/opt/resolve/Developer/Scripting` | `/opt/resolve/libs/Fusion/fusionscript.so` |

### API Compatibility Notes

- **Free version:** External scripting does NOT work. API calls return `None` or fail silently.
- **Python version:** Python 3.10–3.12 recommended. Python 3.13+ may have ABI incompatibilities with Resolve's `fusionscript` library.
- **Resolve must be running:** The API connects to an already-running instance of Resolve.
- **Keyframe mode:** Some timeline operations behave differently depending on `GetKeyframeMode()` / `SetKeyframeMode()` setting.

### Method Naming Conventions

- Methods returning `Bool` are exposed as **POST** (write actions)
- Methods returning data are exposed as **GET**
- Methods that can both read and write use **POST** with optional body

### Render Settings Keys

`SetRenderSettings()` supports these keys:
```
SelectAllFrames, MarkIn, MarkOut, TargetDir, CustomName,
ExportVideo, ExportAudio, ExportCaption, ViewMode,
ReferenceClip, Resolution, FrameRate, TimecodeStart
```

### Audio Sync Settings

`AutoSyncAudio()` accepts these keys:
```
algorithm (int), alignMethod (int), slideMode (int),
ignoreAudio (bool), sampleRate (int), startOffset (int),
duration (int), threshold (float), fadeLength (float),
fadeCurve (int), silences (bool)
```
