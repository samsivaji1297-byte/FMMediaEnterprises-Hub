Yeah, exactly. Right now, everything goes through that single, core rendering engine inside MediaFactory:
 * video_builder.py: The main compositing engine (MoviePy + ImageMagick) that handles font safe-zones, dynamic text wrapping, dark overlay masks, audio syncing, and final video assembly.
 * video_fetcher.py: The B-roll fetcher that queries Pexels for vertical HD stock clips and handles local chunk streaming into cache.
 * design_tokens.py: Holds your core visual layout configurations (1080x1920 canvas sizes, FPS, palette themes, and font path resolvers).
Everything else—whether it's the MediaFactoryBridge or main.py—just acts as a controller passing script payloads into that single rendering pipeline.
Having that unified setup is actually a massive advantage. When we fix or upgrade something (like we just did with text wrapping and B-roll fetching), it instantly upgrades every single post without needing to maintain separate video generation scripts for different styles or platforms.
