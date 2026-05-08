{{- define "oj.name" -}}
{{- .Chart.Name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "oj.fullname" -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}-{{ include "oj.name" . }}
{{- end }}
