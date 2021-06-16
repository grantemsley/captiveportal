# Copyright (C) 2021 Grant Emsley <grant@emsley.ca>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#            http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django.urls import path
from . import views

app_name = 'voucher'

urlpatterns = [
    path('', views.PortalListView.as_view(), name='index'),
    path('portals/<int:portal_id>/', views.printselection, name='portal'),
    path('print/<int:portal_id>/<int:roll_id>/<int:printtemplate_id>/', views.print, name='print'),
]
