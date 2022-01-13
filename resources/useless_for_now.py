    def request_media_with_authorisation(
            self,
            key: str,
            method: str = "GET",
            service: str = "s3",
    ):
        """
        Reference: https://docs.aws.amazon.com/general/latest/gr/sigv4-signed-request-examples.html

        :return:
        """

        endpoint_uri = self.get_file_s3_url(key)
        canonical_uri = self.get_file_s3_canonical_uri(key)
        t = datetime.datetime.utcnow()
        amzdate = t.strftime('%Y%m%dT%H%M%SZ')
        datestamp = t.strftime('%Y%m%d')  # Date w/o time, used in credential scope

        canonical_querystring = 'Action=DescribeRegions&Version=2013-10-15'
        canonical_headers = f'host:{self.file_io.host}\nx-amz-date:{amzdate}\n'
        signed_headers = 'host;x-amz-date'
        payload_hash = hashlib.sha256(''.encode('utf-8')).hexdigest()
        canonical_request = f'{method}\n{canonical_uri}\n{canonical_querystring}\n{canonical_headers}\n{signed_headers}\n{payload_hash}'

        algorithm = 'AWS4-HMAC-SHA256'
        credential_scope = f'{datestamp}/{AWS_REGION}/{service}/aws4_request'
        string_to_sign = f'{algorithm}\n{amzdate}\n{credential_scope}\n{hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()}'
        signing_key = _get_signature_key(self.file_io.aws_secret_access_key, datestamp, AWS_REGION, service)
        signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()

        authorization_header = f'{algorithm} Credential={self.file_io.aws_access_key_id}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}'

        headers = {'x-amz-date': amzdate, 'Authorization': authorization_header}

        return requests.get(
            f"{endpoint_uri}?{canonical_querystring}",
            headers=headers
        )


# Key derivation functions. See:
# http://docs.aws.amazon.com/general/latest/gr/signature-v4-examples.html#signature-v4-examples-python
def _sign(key, msg):
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()


def _get_signature_key(key,
                       date_stamp,
                       service_name="s3",
                       region_name="us-east-1"
                       ):
    k_date = _sign(('AWS4' + key).encode('utf-8'), date_stamp)
    k_region = _sign(k_date, region_name)
    k_service = _sign(k_region, service_name)
    k_signing = _sign(k_service, 'aws4_request')
    return k_signing
