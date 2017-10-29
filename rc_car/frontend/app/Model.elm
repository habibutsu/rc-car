module Model exposing (..)

import Json.Decode
import Json.Encode
--import Json.Decode.Pipeline exposing (decode, required)

type alias Flags =
  { sys_url : String
  }

type alias Sensors =
  { throttle: Float
  , rudder: Int
  , radar: Float
  , accelerometer: List Float
  --, speed: Int
  --, driving_mode: DrivingMode
  }


type DrivingMode
  = Self
  | Record
  | Free


type HeadLampState
  = On
  | Off


type alias Prameters =
  { mode: DrivingMode
  , delay: Maybe Int
  , headlamp: HeadLampState
  }


fromStringDrivingMode : String -> Json.Decode.Decoder DrivingMode
fromStringDrivingMode string =
  case string of
    "self" ->
        Json.Decode.succeed Self
    "record" ->
        Json.Decode.succeed Record
    "free" ->
        Json.Decode.succeed Free
    somethingElse ->
        Json.Decode.fail <| "Unknown mode: " ++ somethingElse


decodeDrivingMode : Json.Decode.Decoder DrivingMode
decodeDrivingMode =
  Json.Decode.string
    |> Json.Decode.andThen fromStringDrivingMode


fromStringHeadLampState : String -> Json.Decode.Decoder HeadLampState
fromStringHeadLampState string =
  case string of
    "on" ->
        Json.Decode.succeed On
    "off" ->
        Json.Decode.succeed Off
    somethingElse ->
        Json.Decode.fail <| "Unknown state: " ++ somethingElse


decodeHeadLampState : Json.Decode.Decoder HeadLampState
decodeHeadLampState =
  Json.Decode.string
    |> Json.Decode.andThen fromStringHeadLampState


parametersJsonDecoder =
  Json.Decode.map3 Prameters
    (Json.Decode.field "mode" decodeDrivingMode)
    (Json.Decode.field "delay" (Json.Decode.nullable Json.Decode.int))
    (Json.Decode.field "headlamp" decodeHeadLampState)

{-encodeDrivingMode : DrivingMode -> Json.Decode.Value
encodeDrivingMode =
  toString >> Json.Encode.string-}

carJsonDecoder =
  Json.Decode.map4 Sensors
    (Json.Decode.field "throttle" Json.Decode.float)
    (Json.Decode.field "rudder" Json.Decode.int)
    (Json.Decode.field "radar" Json.Decode.float)
    (Json.Decode.field "accelerometer" (Json.Decode.list Json.Decode.float))


{-carJsonDecoder =
  decode Car
    |> required "accelerator" JsonDecode.int
    |> required "steering" JsonDecode.int
    |> required "speed" JsonDecode.int
-}
type alias Model =
  { flags: Flags
  , sensors: Sensors
  , parameters: Prameters
  }


type alias Error =
  { message: String
  }


init : Flags -> Model
init flags =
  Model flags (Sensors 0 0 0 [0,0,0]) (Prameters Free Nothing Off)
