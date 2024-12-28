from dataclasses import Field, MISSING


class ClassyField(Field):
    """Wrapper to python standard dataclass adding the encoder, decoder, and is_static properties."""

    def __init__(
        self,
        default,
        default_factory,
        encoder,
        decoder,
        is_static,
        init,
        repr,
        hash,
        compare,
        metadata,
        kw_only,
    ):
        super().__init__(
            default, default_factory, init, repr, hash, compare, metadata, kw_only
        )
        self.encoder: function = encoder
        self.decoder: function = decoder
        self.is_static: bool = is_static


def classy_field(
    *,
    default=MISSING,
    default_factory=MISSING,
    encoder=None,
    decoder=None,
    is_static=False,
    init=True,
    repr=True,
    hash=None,
    compare=True,
    metadata=None,
    kw_only=MISSING,
):
    """
    Facade factory for the ClassyField class.
    """

    if default is not MISSING and default_factory is not MISSING:
        raise ValueError("cannot specify both default and default_factory")
    return ClassyField(
        default,
        default_factory,
        encoder,
        decoder,
        is_static,
        init,
        repr,
        hash,
        compare,
        metadata,
        kw_only,
    )
