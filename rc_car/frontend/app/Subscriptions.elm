module Subscriptions exposing (..)

import WebSocket
import Keyboard
import Mouse

import Model exposing (..)
import Constants exposing (echoServer)


type Msg
    = MouseMsg Mouse.Position
    | ButtonClick String
    | ChangeMode String
    | SwitchHeadlamp
    | ChangeDelay String
    | KeyMsg Keyboard.KeyCode
    | WebsocketMsg String


subscriptions : Model -> Sub Msg
subscriptions model =
  Sub.batch
    [ Mouse.clicks MouseMsg
    , Keyboard.downs KeyMsg
    , WebSocket.listen model.flags.sys_url WebsocketMsg
    ]