from rest_framework import serializers


class RunCreateSerializer(serializers.Serializer):
    topic = serializers.CharField(max_length=200)

    def validate_topic(self, value: str) -> str:
        value = value.strip()
        if len(value) < 2 or len(value) > 200:
            raise serializers.ValidationError("Topic must be 2–200 characters.")
        return value
