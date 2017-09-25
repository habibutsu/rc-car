module Main exposing (..)

import Html

import Model
import Update
import View
import Subscriptions

init : Model.Flags -> ( Model.Model, Cmd Subscriptions.Msg )
init flags =
    let
        init_with_flags = Model.init flags
    in
        (init_with_flags, Cmd.none)

main =
  Html.programWithFlags
    { init = init
    , view = View.view
    , update = Update.update
    , subscriptions = Subscriptions.subscriptions
    }
