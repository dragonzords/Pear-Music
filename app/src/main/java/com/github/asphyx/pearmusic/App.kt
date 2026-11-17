package com.github.asphyx.pearmusic

import android.app.Application
import coil3.ImageLoader
import coil3.PlatformContext
import coil3.SingletonImageLoader
import coil3.request.crossfade
import dagger.hilt.android.HiltAndroidApp

@HiltAndroidApp
class App : Application(), SingletonImageLoader.Factory {
    override fun onCreate() {
        super.onCreate()
        com.github.asphyx.pearmusic.data.ProblemReport.init(this)
        com.enes.innertube.InnerTube.logger = { android.util.Log.i("PearMusic", it) }
        com.github.asphyx.pearmusic.data.ImagePrefetcher.init(this)
        com.github.asphyx.pearmusic.data.LyricsStore.init(this)
        com.github.asphyx.pearmusic.data.OfflineArt.init(this)
        com.github.asphyx.pearmusic.data.LyricsTranslator.init(this)
        com.github.asphyx.pearmusic.data.NewReleases.init(this)
        com.github.asphyx.pearmusic.data.AutoBackup.init(this)
        com.github.asphyx.pearmusic.data.AppUpdater.init(this)
        com.github.asphyx.pearmusic.data.Shortcuts.refresh(this)
    }

    override fun newImageLoader(context: PlatformContext): ImageLoader =
        ImageLoader.Builder(context)
            .crossfade(160)
            // Covers of songs you have offline come from their saved file.
            .components { add(com.github.asphyx.pearmusic.data.OfflineArt.CoilInterceptor) }
            // Big caches: covers come back instantly when you scroll back or reopen a page.
            .memoryCache { coil3.memory.MemoryCache.Builder().maxSizePercent(context, 0.3).build() }
            .diskCache {
                coil3.disk.DiskCache.Builder()
                    .directory(okio.Path.Companion.run { context.cacheDir.resolve("artwork").absolutePath.toPath() })
                    .maxSizeBytes(1024L * 1024 * 1024)
                    .build()
            }
            .build()
}
