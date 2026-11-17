package com.github.asphyx.pearmusic.ui.browse

import com.github.asphyx.pearmusic.ui.theme.tr
import androidx.compose.runtime.Composable
import androidx.hilt.navigation.compose.hiltViewModel
import com.github.asphyx.pearmusic.data.AuthStore
import com.github.asphyx.pearmusic.data.MusicRepository
import com.github.asphyx.pearmusic.ui.home.FeedScreen
import com.github.asphyx.pearmusic.ui.home.FeedViewModel
import dagger.hilt.android.lifecycle.HiltViewModel
import javax.inject.Inject

@HiltViewModel
class BrowseViewModel @Inject constructor(
    repository: MusicRepository,
    auth: AuthStore,
) : FeedViewModel(
    repository, auth,
    listOf(
        "Rock" to "rock hits",
        "R&B / Soul" to "rnb soul hits",
        "Electronic" to "electronic dance hits",
    ),
) {
    override suspend fun primary() = repository.explore().getOrDefault(emptyList())
}

/** The "New" tab: new releases, trending, charts. */
@Composable
fun BrowseScreen(viewModel: BrowseViewModel = hiltViewModel()) {
    FeedScreen(tr("New", "Yeni"), viewModel, showRecents = false, style = com.github.asphyx.pearmusic.ui.components.FeedStyle.New)
}
