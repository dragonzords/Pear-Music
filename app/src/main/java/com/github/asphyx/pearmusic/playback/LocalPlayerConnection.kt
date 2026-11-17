package com.github.asphyx.pearmusic.playback

import androidx.compose.runtime.compositionLocalOf

/** Lets any composable reach the shared player without prop-drilling. */
val LocalPlayerConnection = compositionLocalOf<PlayerConnection?> { null }
