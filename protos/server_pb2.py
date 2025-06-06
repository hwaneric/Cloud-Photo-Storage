# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: server.proto
# Protobuf Python Version: 5.29.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    29,
    0,
    '',
    'server.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0cserver.proto\x12\x06server\":\n\x16StandardServerResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t\"J\n\x0fUserAuthRequest\x12\x10\n\x08username\x18\x01 \x01(\t\x12\x10\n\x08password\x18\x02 \x01(\t\x12\x13\n\x0b\x66rom_client\x18\x03 \x01(\x08\"R\n\x10UserLoginSuccess\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t\x12\x1c\n\x14unread_message_count\x18\x03 \x01(\x05\"\x7f\n\x11UserLoginResponse\x12+\n\x07success\x18\x01 \x01(\x0b\x32\x18.server.UserLoginSuccessH\x00\x12\x31\n\x07\x66\x61ilure\x18\x02 \x01(\x0b\x32\x1e.server.StandardServerResponseH\x00\x42\n\n\x08response\":\n\x11UserLogoutRequest\x12\x10\n\x08username\x18\x01 \x01(\t\x12\x13\n\x0b\x66rom_client\x18\x02 \x01(\x08\"B\n\rListUsernames\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t\x12\x0f\n\x07matches\x18\x03 \x03(\t\"0\n\x14ListUsernamesRequest\x12\x18\n\x10username_pattern\x18\x01 \x01(\t\"\x80\x01\n\x15ListUsernamesResponse\x12(\n\x07success\x18\x01 \x01(\x0b\x32\x15.server.ListUsernamesH\x00\x12\x31\n\x07\x66\x61ilure\x18\x02 \x01(\x0b\x32\x1e.server.StandardServerResponseH\x00\x42\n\n\x08response\"\xa7\x01\n\x12SendMessageRequest\x12\x17\n\x0fsender_username\x18\x01 \x01(\t\x12\x17\n\x0ftarget_username\x18\x02 \x01(\t\x12\x11\n\ttimestamp\x18\x03 \x01(\x05\x12\x0f\n\x07message\x18\x04 \x01(\t\x12\x17\n\nmessage_id\x18\x05 \x01(\tH\x00\x88\x01\x01\x12\x13\n\x0b\x66rom_client\x18\x06 \x01(\x08\x42\r\n\x0b_message_id\"Z\n\x15RegisterClientRequest\x12\x10\n\x08username\x18\x01 \x01(\t\x12\x0c\n\x04host\x18\x02 \x01(\t\x12\x0c\n\x04port\x18\x03 \x01(\x05\x12\x13\n\x0b\x66rom_client\x18\x04 \x01(\x08\"R\n\x13ReadMessagesRequest\x12\x10\n\x08username\x18\x01 \x01(\t\x12\x14\n\x0cnum_messages\x18\x02 \x01(\x05\x12\x13\n\x0b\x66rom_client\x18\x03 \x01(\x08\"W\n\rUnreadMessage\x12\x12\n\nmessage_id\x18\x01 \x01(\t\x12\x0e\n\x06sender\x18\x02 \x01(\t\x12\x11\n\ttimestamp\x18\x03 \x01(\x05\x12\x0f\n\x07message\x18\x04 \x01(\t\"X\n\x0bReadMessage\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t\x12\'\n\x08messages\x18\x03 \x03(\x0b\x32\x15.server.UnreadMessage\"|\n\x13ReadMessageResponse\x12&\n\x07success\x18\x01 \x01(\x0b\x32\x13.server.ReadMessageH\x00\x12\x31\n\x07\x66\x61ilure\x18\x02 \x01(\x0b\x32\x1e.server.StandardServerResponseH\x00\x42\n\n\x08response\"=\n\x14\x44\x65leteAccountRequest\x12\x10\n\x08username\x18\x01 \x01(\t\x12\x13\n\x0b\x66rom_client\x18\x02 \x01(\x08\"X\n\x14\x44\x65leteMessageRequest\x12\x17\n\x0fsender_username\x18\x01 \x01(\t\x12\x12\n\nmessage_id\x18\x02 \x01(\t\x12\x13\n\x0b\x66rom_client\x18\x03 \x01(\x08\",\n\x18\x46\x65tchSentMessagesRequest\x12\x10\n\x08username\x18\x01 \x01(\t\"P\n\x0cSentMessages\x12\x17\n\x0ftarget_username\x18\x01 \x01(\t\x12\'\n\x08messages\x18\x02 \x03(\x0b\x32\x15.server.UnreadMessage\"d\n\x13\x46\x65tchedSentMessages\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t\x12+\n\rsent_messages\x18\x03 \x03(\x0b\x32\x14.server.SentMessages\"\x8a\x01\n\x19\x46\x65tchSentMessagesResponse\x12.\n\x07success\x18\x01 \x01(\x0b\x32\x1b.server.FetchedSentMessagesH\x00\x12\x31\n\x07\x66\x61ilure\x18\x02 \x01(\x0b\x32\x1e.server.StandardServerResponseH\x00\x42\n\n\x08response\"8\n\x10HeartbeatRequest\x12\x11\n\tserver_id\x18\x01 \x01(\x05\x12\x11\n\ttimestamp\x18\x02 \x01(\x03\")\n\x11HeartbeatResponse\x12\x14\n\x0c\x61\x63knowledged\x18\x01 \x01(\x08\"\x16\n\x14\x43urrentLeaderRequest\"\'\n\x15\x43urrentLeaderResponse\x12\x0e\n\x06leader\x18\x01 \x01(\x05\"\"\n\rStatusRequest\x12\x11\n\tserver_id\x18\x01 \x01(\x05\"!\n\x0eStatusResponse\x12\x0f\n\x07is_dead\x18\x01 \x01(\x08\"e\n\rImageMetadata\x12\x10\n\x08username\x18\x01 \x01(\t\x12\x12\n\nimage_name\x18\x02 \x01(\t\x12\x0c\n\x04size\x18\x03 \x01(\x05\x12\x11\n\tfile_type\x18\x04 \x01(\t\x12\r\n\x05\x61lbum\x18\x05 \x01(\t\"m\n\nImageChunk\x12)\n\x08metadata\x18\x01 \x01(\x0b\x32\x15.server.ImageMetadataH\x00\x12\x14\n\nimage_data\x18\x02 \x01(\x0cH\x00\x12\x13\n\x0b\x66rom_client\x18\x03 \x01(\x08\x42\t\n\x07payload\"O\n\x12\x43reateAlbumRequest\x12\x10\n\x08username\x18\x01 \x01(\t\x12\x12\n\nalbum_name\x18\x02 \x01(\t\x12\x13\n\x0b\x66rom_client\x18\x03 \x01(\x08\"u\n\x15\x41\x64\x64\x41lbumEditorRequest\x12\x1a\n\x12requestor_username\x18\x01 \x01(\t\x12\x17\n\x0f\x65\x64itor_username\x18\x02 \x01(\t\x12\x12\n\nalbum_name\x18\x03 \x01(\t\x12\x13\n\x0b\x66rom_client\x18\x04 \x01(\x08\"x\n\x18RemoveAlbumEditorRequest\x12\x1a\n\x12requestor_username\x18\x01 \x01(\t\x12\x17\n\x0f\x65\x64itor_username\x18\x02 \x01(\t\x12\x12\n\nalbum_name\x18\x03 \x01(\t\x12\x13\n\x0b\x66rom_client\x18\x04 \x01(\x08\"O\n\x12\x44\x65leteAlbumRequest\x12\x10\n\x08username\x18\x01 \x01(\t\x12\x12\n\nalbum_name\x18\x02 \x01(\t\x12\x13\n\x0b\x66rom_client\x18\x03 \x01(\x08\"c\n\x12\x44\x65leteImageRequest\x12\x10\n\x08username\x18\x01 \x01(\t\x12\x12\n\nimage_name\x18\x02 \x01(\t\x12\x12\n\nalbum_name\x18\x03 \x01(\t\x12\x13\n\x0b\x66rom_client\x18\x04 \x01(\x08\"p\n\x12\x46\x65tchPhotosRequest\x12\x10\n\x08username\x18\x01 \x01(\t\x12\x12\n\nalbum_name\x18\x02 \x01(\t\x12\x0c\n\x04page\x18\x03 \x01(\x05\x12\x11\n\tpage_size\x18\x04 \x01(\x05\x12\x13\n\x0b\x66rom_client\x18\x05 \x01(\x08\"?\n\x16\x46\x65tchUserAlbumsRequest\x12\x10\n\x08username\x18\x01 \x01(\t\x12\x13\n\x0b\x66rom_client\x18\x02 \x01(\x08\"K\n\x17\x46\x65tchUserAlbumsResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t\x12\x0e\n\x06\x61lbums\x18\x03 \x03(\t\"@\n\x18\x46\x65tchAlbumEditorsRequest\x12\x10\n\x08username\x18\x01 \x01(\t\x12\x12\n\nalbum_name\x18\x02 \x01(\t\"N\n\x19\x46\x65tchAlbumEditorsResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t\x12\x0f\n\x07\x65\x64itors\x18\x03 \x03(\t2\xfe\t\n\x06Server\x12\x41\n\x06Signup\x12\x17.server.UserAuthRequest\x1a\x1e.server.StandardServerResponse\x12;\n\x05Login\x12\x17.server.UserAuthRequest\x1a\x19.server.UserLoginResponse\x12\x43\n\x06Logout\x12\x19.server.UserLogoutRequest\x1a\x1e.server.StandardServerResponse\x12L\n\rListUsernames\x12\x1c.server.ListUsernamesRequest\x1a\x1d.server.ListUsernamesResponse\x12M\n\rDeleteAccount\x12\x1c.server.DeleteAccountRequest\x1a\x1e.server.StandardServerResponse\x12\x42\n\tHeartbeat\x12\x18.server.HeartbeatRequest\x1a\x19.server.HeartbeatResponse(\x01\x12L\n\rCurrentLeader\x12\x1c.server.CurrentLeaderRequest\x1a\x1d.server.CurrentLeaderResponse\x12\x43\n\x12\x43onfirmServerDeath\x12\x15.server.StatusRequest\x1a\x16.server.StatusResponse\x12\x43\n\x0bUploadImage\x12\x12.server.ImageChunk\x1a\x1e.server.StandardServerResponse(\x01\x12I\n\x0b\x43reateAlbum\x12\x1a.server.CreateAlbumRequest\x1a\x1e.server.StandardServerResponse\x12O\n\x0e\x41\x64\x64\x41lbumEditor\x12\x1d.server.AddAlbumEditorRequest\x1a\x1e.server.StandardServerResponse\x12U\n\x11RemoveAlbumEditor\x12 .server.RemoveAlbumEditorRequest\x1a\x1e.server.StandardServerResponse\x12I\n\x0b\x44\x65leteAlbum\x12\x1a.server.DeleteAlbumRequest\x1a\x1e.server.StandardServerResponse\x12I\n\x0b\x44\x65leteImage\x12\x1a.server.DeleteImageRequest\x1a\x1e.server.StandardServerResponse\x12?\n\x0b\x46\x65tchPhotos\x12\x1a.server.FetchPhotosRequest\x1a\x12.server.ImageChunk0\x01\x12R\n\x0f\x46\x65tchUserAlbums\x12\x1e.server.FetchUserAlbumsRequest\x1a\x1f.server.FetchUserAlbumsResponse\x12X\n\x11\x46\x65tchAlbumEditors\x12 .server.FetchAlbumEditorsRequest\x1a!.server.FetchAlbumEditorsResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'server_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_STANDARDSERVERRESPONSE']._serialized_start=24
  _globals['_STANDARDSERVERRESPONSE']._serialized_end=82
  _globals['_USERAUTHREQUEST']._serialized_start=84
  _globals['_USERAUTHREQUEST']._serialized_end=158
  _globals['_USERLOGINSUCCESS']._serialized_start=160
  _globals['_USERLOGINSUCCESS']._serialized_end=242
  _globals['_USERLOGINRESPONSE']._serialized_start=244
  _globals['_USERLOGINRESPONSE']._serialized_end=371
  _globals['_USERLOGOUTREQUEST']._serialized_start=373
  _globals['_USERLOGOUTREQUEST']._serialized_end=431
  _globals['_LISTUSERNAMES']._serialized_start=433
  _globals['_LISTUSERNAMES']._serialized_end=499
  _globals['_LISTUSERNAMESREQUEST']._serialized_start=501
  _globals['_LISTUSERNAMESREQUEST']._serialized_end=549
  _globals['_LISTUSERNAMESRESPONSE']._serialized_start=552
  _globals['_LISTUSERNAMESRESPONSE']._serialized_end=680
  _globals['_SENDMESSAGEREQUEST']._serialized_start=683
  _globals['_SENDMESSAGEREQUEST']._serialized_end=850
  _globals['_REGISTERCLIENTREQUEST']._serialized_start=852
  _globals['_REGISTERCLIENTREQUEST']._serialized_end=942
  _globals['_READMESSAGESREQUEST']._serialized_start=944
  _globals['_READMESSAGESREQUEST']._serialized_end=1026
  _globals['_UNREADMESSAGE']._serialized_start=1028
  _globals['_UNREADMESSAGE']._serialized_end=1115
  _globals['_READMESSAGE']._serialized_start=1117
  _globals['_READMESSAGE']._serialized_end=1205
  _globals['_READMESSAGERESPONSE']._serialized_start=1207
  _globals['_READMESSAGERESPONSE']._serialized_end=1331
  _globals['_DELETEACCOUNTREQUEST']._serialized_start=1333
  _globals['_DELETEACCOUNTREQUEST']._serialized_end=1394
  _globals['_DELETEMESSAGEREQUEST']._serialized_start=1396
  _globals['_DELETEMESSAGEREQUEST']._serialized_end=1484
  _globals['_FETCHSENTMESSAGESREQUEST']._serialized_start=1486
  _globals['_FETCHSENTMESSAGESREQUEST']._serialized_end=1530
  _globals['_SENTMESSAGES']._serialized_start=1532
  _globals['_SENTMESSAGES']._serialized_end=1612
  _globals['_FETCHEDSENTMESSAGES']._serialized_start=1614
  _globals['_FETCHEDSENTMESSAGES']._serialized_end=1714
  _globals['_FETCHSENTMESSAGESRESPONSE']._serialized_start=1717
  _globals['_FETCHSENTMESSAGESRESPONSE']._serialized_end=1855
  _globals['_HEARTBEATREQUEST']._serialized_start=1857
  _globals['_HEARTBEATREQUEST']._serialized_end=1913
  _globals['_HEARTBEATRESPONSE']._serialized_start=1915
  _globals['_HEARTBEATRESPONSE']._serialized_end=1956
  _globals['_CURRENTLEADERREQUEST']._serialized_start=1958
  _globals['_CURRENTLEADERREQUEST']._serialized_end=1980
  _globals['_CURRENTLEADERRESPONSE']._serialized_start=1982
  _globals['_CURRENTLEADERRESPONSE']._serialized_end=2021
  _globals['_STATUSREQUEST']._serialized_start=2023
  _globals['_STATUSREQUEST']._serialized_end=2057
  _globals['_STATUSRESPONSE']._serialized_start=2059
  _globals['_STATUSRESPONSE']._serialized_end=2092
  _globals['_IMAGEMETADATA']._serialized_start=2094
  _globals['_IMAGEMETADATA']._serialized_end=2195
  _globals['_IMAGECHUNK']._serialized_start=2197
  _globals['_IMAGECHUNK']._serialized_end=2306
  _globals['_CREATEALBUMREQUEST']._serialized_start=2308
  _globals['_CREATEALBUMREQUEST']._serialized_end=2387
  _globals['_ADDALBUMEDITORREQUEST']._serialized_start=2389
  _globals['_ADDALBUMEDITORREQUEST']._serialized_end=2506
  _globals['_REMOVEALBUMEDITORREQUEST']._serialized_start=2508
  _globals['_REMOVEALBUMEDITORREQUEST']._serialized_end=2628
  _globals['_DELETEALBUMREQUEST']._serialized_start=2630
  _globals['_DELETEALBUMREQUEST']._serialized_end=2709
  _globals['_DELETEIMAGEREQUEST']._serialized_start=2711
  _globals['_DELETEIMAGEREQUEST']._serialized_end=2810
  _globals['_FETCHPHOTOSREQUEST']._serialized_start=2812
  _globals['_FETCHPHOTOSREQUEST']._serialized_end=2924
  _globals['_FETCHUSERALBUMSREQUEST']._serialized_start=2926
  _globals['_FETCHUSERALBUMSREQUEST']._serialized_end=2989
  _globals['_FETCHUSERALBUMSRESPONSE']._serialized_start=2991
  _globals['_FETCHUSERALBUMSRESPONSE']._serialized_end=3066
  _globals['_FETCHALBUMEDITORSREQUEST']._serialized_start=3068
  _globals['_FETCHALBUMEDITORSREQUEST']._serialized_end=3132
  _globals['_FETCHALBUMEDITORSRESPONSE']._serialized_start=3134
  _globals['_FETCHALBUMEDITORSRESPONSE']._serialized_end=3212
  _globals['_SERVER']._serialized_start=3215
  _globals['_SERVER']._serialized_end=4493
# @@protoc_insertion_point(module_scope)
